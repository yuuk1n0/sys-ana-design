from pathlib import Path
import re
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PhaseThreeBusinessClosureTests(unittest.TestCase):
    def test_business_closure_routes_and_frontend_helpers_are_registered(self):
        expected_paths = {
            "/sale/submit",
            "/sale/return",
            "/sale/order/list",
            "/sale/order/get",
            "/inventory/operate",
        }

        sales_api_content = (PROJECT_ROOT / "app/api/v1/sales/sales.py").read_text(encoding="utf-8")
        inventory_api_content = (
            PROJECT_ROOT / "app/api/v1/inventories/inventories.py"
        ).read_text(encoding="utf-8")
        v1_content = (PROJECT_ROOT / "app/api/v1/__init__.py").read_text(encoding="utf-8")

        for path in ["/submit", "/return", "/order/list", "/order/get"]:
            self.assertIn(path, sales_api_content, f"销售路由缺失: {path}")
        self.assertIn("/operate", inventory_api_content, "库存作业路由缺失: /operate")
        self.assertIn('include_router(sales_router, prefix="/sale"', v1_content, "销售路由未注册到 v1")

        api_content = (PROJECT_ROOT / "web/src/api/index.js").read_text(encoding="utf-8")
        frontend_paths = set(re.findall(r"request\.(?:get|post|delete)\('([^']+)'", api_content))
        for path in expected_paths:
            self.assertIn(path, frontend_paths, f"前端 API 缺少业务闭环接口: {path}")

    def test_sales_and_inventory_pages_expose_real_operation_entries(self):
        sales_content = (PROJECT_ROOT / "web/src/views/store/sales/index.vue").read_text(encoding="utf-8")
        inventory_txn_content = (
            PROJECT_ROOT / "web/src/views/store/inventory-txn/index.vue"
        ).read_text(encoding="utf-8")

        for keyword in ["销售开单", "退货录入", "业务单据", "submitSaleOrder", "submitReturnOrder"]:
            self.assertIn(keyword, sales_content, f"销售页面缺少关键能力: {keyword}")

        for keyword in ["入库登记", "出库登记", "createInventoryOperation", "STOCK_IN", "STOCK_OUT"]:
            self.assertIn(keyword, inventory_txn_content, f"库存流水页面缺少关键能力: {keyword}")
