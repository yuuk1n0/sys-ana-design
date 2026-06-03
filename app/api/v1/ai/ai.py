from __future__ import annotations

import json
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter

from app.api.v1.workbench.workbench import _build_ai_panel, _build_store_metrics, _day_range
from app.controllers.finance import finance_controller
from app.models.admin import Dept
from app.schemas import Success
from app.schemas.ai import AIChatRequest
from app.settings.config import settings

router = APIRouter()


async def _resolve_store_for_chat(store_id: int | None):
    if store_id is None:
        return None
    return await Dept.filter(id=store_id, is_deleted=False).first()


async def _call_openai_compatible(messages: list[dict]):
    if not settings.LLM_BASE_URL or not settings.LLM_API_KEY:
        return None, {"enabled": False}

    base_url = settings.LLM_BASE_URL.rstrip("/")
    if base_url.endswith("/v1"):
        url_candidates = [base_url + "/chat/completions", base_url + "/chat/completions/"]
    else:
        url_candidates = [
            base_url + "/v1/chat/completions",
            base_url + "/v1/chat/completions/",
            base_url + "/chat/completions",
            base_url + "/chat/completions/",
        ]
    headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}"}
    payload = {"model": settings.LLM_MODEL, "messages": messages, "temperature": 0.2}
    timeout = httpx.Timeout(settings.LLM_TIMEOUT_SECONDS)
    debug = {
        "enabled": True,
        "base_url": settings.LLM_BASE_URL,
        "model": settings.LLM_MODEL,
        "timeout_seconds": settings.LLM_TIMEOUT_SECONDS,
        "attempts": [],
        "error": None,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        last_error = None
        for url in url_candidates:
            try:
                res = await client.post(url, json=payload, headers=headers)
                body_preview = (res.text or "")[:300]
                debug["attempts"].append({"url": url, "status_code": res.status_code, "body": body_preview})

                if res.status_code == 200:
                    data = res.json()
                    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
                    if not content:
                        content = data.get("output") or data.get("response") or data.get("text")

                    if isinstance(content, str) and content.strip():
                        return content, {**debug, "ok": True}

                    last_error = {"type": "empty_content", "body": str(data)[:300]}
                    continue

                if res.status_code == 404:
                    last_error = {"type": "http_404", "body": body_preview}
                    continue

                if res.status_code == 401:
                    last_error = {"type": "http_401", "body": body_preview}
                    break

                if res.status_code == 402:
                    last_error = {"type": "http_402", "body": body_preview}
                    break

                if res.status_code == 429:
                    last_error = {"type": "http_429", "body": body_preview}
                    break

                last_error = {"type": f"http_{res.status_code}", "body": body_preview}
                break
            except (httpx.HTTPError, ValueError, TypeError) as e:
                err_preview = str(e)[:300]
                last_error = {"type": e.__class__.__name__, "body": err_preview}
                debug["attempts"].append({"url": url, "status_code": None, "body": err_preview})

        debug["error"] = last_error or {"type": "unknown", "body": ""}
        debug["ok"] = False
        return None, debug


def _fallback_reply(question: str, store_name: str, store_metrics: dict, kpis: dict, ai_panel: dict):
    today_sales = float(kpis.get("today_sales_amount") or 0.0)
    yesterday_sales = float(kpis.get("yesterday_sales_amount") or 0.0)
    inv_warn = int(store_metrics.get("inventory_warning_count") or 0)
    member_count = int(store_metrics.get("member_count") or 0)

    lines = [
        f"门店：{store_name}",
        f"今日净销售额：¥{today_sales:,.2f}",
        f"昨日净销售额：¥{yesterday_sales:,.2f}",
        f"库存预警SKU：{inv_warn}",
        f"会员数：{member_count}",
        "",
        f"你的问题：{question}",
    ]
    if ai_panel.get("warnings"):
        lines.append("")
        lines.append("异常预警：")
        for item in ai_panel["warnings"]:
            lines.append(f"- {item}")
    if ai_panel.get("suggestions"):
        lines.append("")
        lines.append("智能建议：")
        for item in ai_panel["suggestions"]:
            lines.append(f"- {item}")
    return "\n".join(lines)


@router.post("/operate/chat", summary="AI智能经营分析对话")
async def operate_ai_chat(req: AIChatRequest):
    store_obj = await _resolve_store_for_chat(req.store_id)
    store_id = store_obj.id if store_obj else None
    store_name = store_obj.name if store_obj else "未指定门店"

    if store_id is None:
        return Success(
            data={
                "reply": "请先选择/绑定门店后再进行经营分析对话。",
                "analysis": {"summary": "缺少门店上下文。", "warnings": [], "suggestions": []},
            }
        )

    store_metrics = await _build_store_metrics(store_id, store_name)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    today_start, today_end = _day_range(today)
    yesterday_start, yesterday_end = _day_range(yesterday)
    today_overview = await finance_controller.get_overview(store_id=store_id, start_time=today_start, end_time=today_end)
    yesterday_overview = await finance_controller.get_overview(store_id=store_id, start_time=yesterday_start, end_time=yesterday_end)
    kpis = {
        "today_sales_amount": float(today_overview.get("net_sales_amount") or 0.0),
        "yesterday_sales_amount": float(yesterday_overview.get("net_sales_amount") or 0.0),
        "gross_margin_rate": None,
        "inventory_warning_count": int(store_metrics.get("inventory_warning_count") or 0),
    }
    ai_panel = await _build_ai_panel(store_metrics, kpis)

    context = {
        "store": {
            "store_id": store_id,
            "store_name": store_name,
            "inventory_warning_count": store_metrics.get("inventory_warning_count"),
            "inventory_qty": store_metrics.get("inventory_qty"),
            "inventory_sku_count": store_metrics.get("inventory_sku_count"),
            "member_count": store_metrics.get("member_count"),
            "member_points": store_metrics.get("member_points"),
            "net_sales_amount": store_metrics.get("net_sales_amount"),
            "sales_order_count": store_metrics.get("sales_order_count"),
        },
        "kpis": kpis,
        "analysis": ai_panel,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    system_prompt = (
        "你是连锁超市门店的AI经营分析助手。"
        "你会基于给定的门店经营数据，回答用户问题，并输出可执行的诊断与建议。"
        "不要编造不存在的数据；如数据缺失，请明确指出缺口与可补充的数据口径。"
    )
    llm_messages = [{"role": "system", "content": system_prompt}]
    llm_messages.append({"role": "system", "content": "门店经营数据(JSON)：\n" + json.dumps(context, ensure_ascii=False)})
    for item in req.messages:
        llm_messages.append(item.model_dump())
    llm_messages.append({"role": "user", "content": req.question})

    reply, llm_debug = await _call_openai_compatible(llm_messages)
    if not reply:
        hint = ""
        if isinstance(llm_debug, dict) and llm_debug.get("enabled") and isinstance(llm_debug.get("error"), dict):
            err_type = llm_debug["error"].get("type")
            if err_type == "http_402":
                hint = "提示：大模型调用失败（Insufficient Balance / 余额不足），已使用本地规则分析结果。\n\n"
            elif err_type == "http_401":
                hint = "提示：大模型调用失败（API Key 无效/无权限），已使用本地规则分析结果。\n\n"
            elif err_type == "http_429":
                hint = "提示：大模型调用失败（请求过于频繁触发限流），已使用本地规则分析结果。\n\n"
        reply = hint + _fallback_reply(req.question, store_name, store_metrics, kpis, ai_panel)

    data = {"reply": reply, "analysis": ai_panel, "context": context}
    if settings.DEBUG:
        data["llm_debug"] = llm_debug
    return Success(data=data)
