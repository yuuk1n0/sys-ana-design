from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.finance import finance_controller
from app.controllers.inventory import inventory_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept, InventoryTxn, Member, Product, ProductCategory, StoreEmployee, StoreInventory, Supplier
from app.schemas import Success

router = APIRouter()


def _day_range(target: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target, time.min)
    end = start + timedelta(days=1)
    return start, end


async def _resolve_current_store():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    if user_obj.dept_id:
        return await Dept.filter(id=user_obj.dept_id, is_deleted=False).first()
    if user_obj.is_superuser:
        return await Dept.filter(is_deleted=False).order_by("id").first()
    return None


async def _build_store_metrics(store_id: int, store_name: str):
    store_metrics = {
        "store_id": store_id,
        "store_name": store_name,
        "category_count": await ProductCategory.filter(store_id=store_id).count(),
        "product_count": await Product.filter(store_id=store_id).count(),
        "inventory_sku_count": 0,
        "inventory_qty": 0,
        "inventory_warning_count": 0,
        "sales_order_count": 0,
        "net_sales_amount": 0.0,
        "member_count": await Member.filter(store_id=store_id).count(),
        "member_points": 0,
        "employee_count": await StoreEmployee.filter(store_id=store_id).count(),
        "supplier_count": await Supplier.filter(store_id=store_id).count(),
    }

    inventory_rows = await StoreInventory.filter(store_id=store_id).all()
    store_metrics["inventory_sku_count"] = len(inventory_rows)
    store_metrics["inventory_qty"] = sum(item.available_qty for item in inventory_rows)
    store_metrics["inventory_warning_count"] = sum(
        1 for item in inventory_rows if item.available_qty <= item.low_stock_threshold
    )

    member_rows = await Member.filter(store_id=store_id).all()
    store_metrics["member_points"] = sum(item.points for item in member_rows)

    sales_rows = await InventoryTxn.filter(store_id=store_id, biz_type__in=["SALE", "RETURN"]).all()
    store_metrics["sales_order_count"] = len({item.biz_no for item in sales_rows})
    store_metrics["net_sales_amount"] = (await finance_controller.get_overview(store_id=store_id))["net_sales_amount"]

    return store_metrics


async def _compute_sales_trend(store_id: int, days: int):
    today = datetime.now().date()
    start_day = today - timedelta(days=days - 1)
    start_time, _ = _day_range(start_day)
    _, end_time = _day_range(today)

    txn_rows = await InventoryTxn.filter(
        Q(store_id=store_id, biz_type__in=["SALE", "RETURN"]) & Q(created_at__gte=start_time) & Q(created_at__lt=end_time)
    ).all()
    product_ids = list({item.product_id for item in txn_rows})
    product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all() if product_ids else []
    product_map = {item.id: item for item in product_rows}

    buckets: dict[date, Decimal] = {today - timedelta(days=i): Decimal("0") for i in range(days)}
    for txn in txn_rows:
        bucket = txn.created_at.date()
        if bucket not in buckets:
            continue
        product = product_map.get(txn.product_id)
        meta = inventory_controller.parse_txn_remark(txn.remark)
        unit_price = Decimal(str(meta.get("unit_price") or (product.sale_price if product else 0)))
        qty = abs(txn.change_qty)
        delta = unit_price * qty
        if txn.biz_type == "SALE":
            buckets[bucket] += delta
        elif txn.biz_type == "RETURN":
            buckets[bucket] -= delta

    points = []
    for i in reversed(range(days)):
        d = today - timedelta(days=i)
        points.append({"date": d.strftime("%Y-%m-%d"), "amount": float(buckets.get(d, Decimal("0")))})
    return points


async def _compute_inventory_distribution(store_id: int, top_n: int = 4):
    inventory_rows = await StoreInventory.filter(store_id=store_id).all()
    product_ids = [item.product_id for item in inventory_rows]
    if not product_ids:
        return []

    product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all()
    product_map = {item.id: item for item in product_rows}
    category_ids = list({item.category_id for item in product_rows})
    category_rows = await ProductCategory.filter(store_id=store_id, id__in=category_ids).all() if category_ids else []
    category_map = {item.id: item.name for item in category_rows}

    grouped = defaultdict(int)
    for inventory in inventory_rows:
        product = product_map.get(inventory.product_id)
        category_name = category_map.get(product.category_id) if product else None
        grouped[category_name or "未分类"] += int(inventory.available_qty)

    items = [{"category": k, "qty": v} for k, v in grouped.items() if v > 0]
    items.sort(key=lambda item: item["qty"], reverse=True)
    if len(items) <= top_n:
        return items

    head = items[:top_n]
    rest_qty = sum(item["qty"] for item in items[top_n:])
    if rest_qty > 0:
        head.append({"category": "其他", "qty": rest_qty})
    return head


async def _compute_hot_goods(store_id: int, days: int, top_k: int = 5):
    today = datetime.now().date()
    start_day = today - timedelta(days=days - 1)
    start_time, _ = _day_range(start_day)
    _, end_time = _day_range(today)

    txn_rows = await InventoryTxn.filter(
        Q(store_id=store_id, biz_type="SALE") & Q(created_at__gte=start_time) & Q(created_at__lt=end_time)
    ).all()
    product_qty = defaultdict(int)
    for txn in txn_rows:
        product_qty[txn.product_id] += abs(int(txn.change_qty))

    ranked = sorted(product_qty.items(), key=lambda item: item[1], reverse=True)[:top_k]
    product_ids = [pid for pid, _ in ranked]
    product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all() if product_ids else []
    product_map = {item.id: item for item in product_rows}
    inventory_rows = await StoreInventory.filter(store_id=store_id, product_id__in=product_ids).all() if product_ids else []
    inventory_map = {item.product_id: item.available_qty for item in inventory_rows}

    res = []
    for product_id, qty in ranked:
        product = product_map.get(product_id)
        res.append(
            {
                "product_id": product_id,
                "name": product.name if product else "",
                "sale_qty": qty,
                "stock_qty": int(inventory_map.get(product_id, 0)),
            }
        )
    return res


async def _compute_store_sales_ranking():
    today = datetime.now().date()
    start_time, end_time = _day_range(today)

    store_rows = await Dept.filter(is_deleted=False).all()
    store_ids = [item.id for item in store_rows]
    store_map = {item.id: item.name for item in store_rows}

    txn_rows = await InventoryTxn.filter(
        Q(store_id__in=store_ids, biz_type__in=["SALE", "RETURN"])
        & Q(created_at__gte=start_time)
        & Q(created_at__lt=end_time)
    ).all()
    product_ids = list({item.product_id for item in txn_rows})
    product_rows = (
        await Product.filter(store_id__in=store_ids, id__in=product_ids).all() if (store_ids and product_ids) else []
    )
    product_map = {(item.store_id, item.id): item for item in product_rows}

    amount_map: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    for txn in txn_rows:
        product = product_map.get((txn.store_id, txn.product_id))
        meta = inventory_controller.parse_txn_remark(txn.remark)
        unit_price = Decimal(str(meta.get("unit_price") or (product.sale_price if product else 0)))
        qty = abs(txn.change_qty)
        delta = unit_price * qty
        if txn.biz_type == "SALE":
            amount_map[txn.store_id] += delta
        elif txn.biz_type == "RETURN":
            amount_map[txn.store_id] -= delta

    ranking = [
        {"store_id": store_id, "store_name": store_map.get(store_id, ""), "net_sales_amount": float(amount)}
        for store_id, amount in amount_map.items()
    ]
    ranking.sort(key=lambda item: item["net_sales_amount"], reverse=True)

    max_amount = max((item["net_sales_amount"] for item in ranking), default=0.0)
    for item in ranking:
        item["percent"] = 0 if max_amount <= 0 else round(item["net_sales_amount"] / max_amount * 100, 2)
    return ranking[:5]


async def _build_ai_panel(store_metrics: dict, kpis: dict):
    warnings = []
    suggestions = []

    inv_warn = int(store_metrics.get("inventory_warning_count") or 0)
    if inv_warn > 0:
        warnings.append(f"当前库存预警 SKU {inv_warn} 个，建议优先处理缺货与临期补货。")
        suggestions.append("按“可用库存 ≤ 预警阈值”拉取清单，优先补齐高动销SKU并同步阈值策略。")

    today_sales = float(kpis.get("today_sales_amount") or 0.0)
    yesterday_sales = float(kpis.get("yesterday_sales_amount") or 0.0)
    if yesterday_sales > 0 and today_sales / yesterday_sales < 0.9:
        warnings.append("今日销售额较昨日明显回落，可能存在客流或缺货影响。")
        suggestions.append("核对热销品库存与价格策略，结合时段客流做促销与陈列调整。")

    member_count = int(store_metrics.get("member_count") or 0)
    if member_count <= 0:
        suggestions.append("当前门店会员数据为空，可先引导收银绑定会员/手机号，提高复购与积分沉淀。")

    summary = "门店经营概览已生成，可在下方对话中进一步追问原因与行动建议。"
    if warnings:
        summary = f"已发现 {len(warnings)} 项经营关注点，建议优先排查库存与销售波动。"

    return {"summary": summary, "warnings": warnings, "suggestions": suggestions}


@router.get("/dashboard", summary="工作台数据驾驶舱")
async def get_workbench_dashboard(days: int = Query(7, ge=1, le=31, description="趋势天数")):
    current_store = await _resolve_current_store()
    dept_count = await Dept.filter(is_deleted=False).count()

    store_id = current_store.id if current_store else None
    store_name = current_store.name if current_store else "未绑定门店"
    store_metrics = {}
    kpis = {}
    sales_trend = []
    inventory_distribution = []
    store_sales_ranking = []
    hot_goods_top5 = []
    ai_panel = {"summary": "请先绑定门店后查看经营分析。", "warnings": [], "suggestions": []}

    if store_id is not None:
        store_metrics = await _build_store_metrics(store_id, store_name)

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        today_start, today_end = _day_range(today)
        yesterday_start, yesterday_end = _day_range(yesterday)
        today_overview = await finance_controller.get_overview(store_id=store_id, start_time=today_start, end_time=today_end)
        yesterday_overview = await finance_controller.get_overview(
            store_id=store_id, start_time=yesterday_start, end_time=yesterday_end
        )

        today_sales = float(today_overview.get("net_sales_amount") or 0.0)
        yesterday_sales = float(yesterday_overview.get("net_sales_amount") or 0.0)
        change_rate = None
        if yesterday_sales > 0:
            change_rate = round((today_sales - yesterday_sales) / yesterday_sales, 4)

        kpis = {
            "today_sales_amount": today_sales,
            "yesterday_sales_amount": yesterday_sales,
            "today_vs_yesterday_rate": change_rate,
            "gross_margin_rate": None,
            "inventory_warning_count": int(store_metrics.get("inventory_warning_count") or 0),
        }

        sales_trend = await _compute_sales_trend(store_id=store_id, days=days)
        inventory_distribution = await _compute_inventory_distribution(store_id=store_id)
        store_sales_ranking = await _compute_store_sales_ranking()
        hot_goods_top5 = await _compute_hot_goods(store_id=store_id, days=days)
        ai_panel = await _build_ai_panel(store_metrics, kpis)

    data = {
        "store": store_metrics or {"store_id": store_id, "store_name": store_name},
        "statistics": {
            "store_count": dept_count,
            "pending_audit_count": 0,
            "system_message_count": 0,
        },
        "kpis": kpis,
        "sales_trend": sales_trend,
        "inventory_distribution": inventory_distribution,
        "store_sales_ranking": store_sales_ranking,
        "hot_goods_top5": hot_goods_top5,
        "ai_panel": ai_panel,
    }
    return Success(
        data={
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "store_id": store_id,
            "store_name": store_name,
            "data": data,
        }
    )

