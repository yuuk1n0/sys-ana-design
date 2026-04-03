from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from tortoise.expressions import Q

from app.models.admin import InventoryTxn, Product


class FinanceController:
    async def get_overview(self, store_id: int, start_time: datetime | None = None, end_time: datetime | None = None):
        q = Q(store_id=store_id, biz_type__in=["SALE", "RETURN"])
        if start_time and end_time:
            q &= Q(created_at__range=[start_time, end_time])
        elif start_time:
            q &= Q(created_at__gte=start_time)
        elif end_time:
            q &= Q(created_at__lte=end_time)
        txn_rows = await InventoryTxn.filter(q).all()
        product_ids = list({item.product_id for item in txn_rows})
        product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all() if product_ids else []
        product_map = {item.id: item for item in product_rows}
        sale_amount = Decimal("0")
        return_amount = Decimal("0")
        net_qty = 0
        for item in txn_rows:
            product = product_map.get(item.product_id)
            if not product:
                continue
            price = Decimal(str(product.sale_price))
            if item.biz_type == "SALE":
                qty = abs(item.change_qty)
                sale_amount += price * qty
                net_qty += qty
            elif item.biz_type == "RETURN":
                qty = abs(item.change_qty)
                return_amount += price * qty
                net_qty -= qty
        net_sales_amount = sale_amount - return_amount
        return {
            "sale_amount": float(sale_amount),
            "return_amount": float(return_amount),
            "net_sales_amount": float(net_sales_amount),
            "net_sales_qty": net_qty,
            "txn_count": len(txn_rows),
        }

    async def get_statement_data(
        self,
        store_id: int,
        page: int,
        page_size: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ):
        q = Q(store_id=store_id, biz_type__in=["SALE", "RETURN"])
        if start_time and end_time:
            q &= Q(created_at__range=[start_time, end_time])
        elif start_time:
            q &= Q(created_at__gte=start_time)
        elif end_time:
            q &= Q(created_at__lte=end_time)
        txn_rows = await InventoryTxn.filter(q).order_by("-created_at").all()
        product_ids = list({item.product_id for item in txn_rows})
        product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all() if product_ids else []
        product_map = {item.id: item for item in product_rows}
        grouped = defaultdict(lambda: {"sale_amount": Decimal("0"), "return_amount": Decimal("0"), "net_qty": 0, "date": ""})
        for item in txn_rows:
            product = product_map.get(item.product_id)
            if not product:
                continue
            bucket = item.created_at.strftime("%Y-%m-%d")
            grouped[bucket]["date"] = bucket
            price = Decimal(str(product.sale_price))
            qty = abs(item.change_qty)
            if item.biz_type == "SALE":
                grouped[bucket]["sale_amount"] += price * qty
                grouped[bucket]["net_qty"] += qty
            elif item.biz_type == "RETURN":
                grouped[bucket]["return_amount"] += price * qty
                grouped[bucket]["net_qty"] -= qty
        rows = []
        for _, value in grouped.items():
            sale_amount = value["sale_amount"]
            return_amount = value["return_amount"]
            rows.append(
                {
                    "date": value["date"],
                    "sale_amount": float(sale_amount),
                    "return_amount": float(return_amount),
                    "net_sales_amount": float(sale_amount - return_amount),
                    "net_sales_qty": value["net_qty"],
                }
            )
        rows.sort(key=lambda item: item["date"], reverse=True)
        total = len(rows)
        paged = rows[(page - 1) * page_size : page * page_size]
        return total, paged


finance_controller = FinanceController()
