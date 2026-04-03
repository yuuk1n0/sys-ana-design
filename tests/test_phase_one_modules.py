import json
import re
import unittest
from unittest.mock import AsyncMock, patch

from app.api.v1 import v1_router
from app.api.v1.finances.finances import get_finance_overview, get_finance_statement_list
from app.api.v1.inventories.inventories import get_inventory_warning_list
from app.api.v1.products.products import list_product


class PhaseOneInterfaceContractTests(unittest.TestCase):
    def test_phase_one_frontend_backend_paths_are_aligned(self):
        expected_paths = {
            "/product/list",
            "/product/get",
            "/product/create",
            "/product/update",
            "/product/change_status",
            "/inventory/balance/list",
            "/inventory/txn/list",
            "/inventory/warning/list",
            "/finance/overview",
            "/finance/statement/list",
        }
        backend_paths = {route.path for route in v1_router.routes}
        for path in expected_paths:
            self.assertIn(path, backend_paths, f"后端缺少一期接口: {path}")
        with open("web/src/api/index.js", "r", encoding="utf-8") as f:
            content = f.read()
        frontend_paths = set(re.findall(r"request\.(?:get|post|delete)\('([^']+)'", content))
        for path in expected_paths:
            self.assertIn(path, frontend_paths, f"前端API缺少一期接口: {path}")


class PhaseOneModuleUnitTests(unittest.IsolatedAsyncioTestCase):
    async def test_product_list_response_shape(self):
        mock_rows = [{"id": 1, "name": "可乐", "available_qty": 20}]
        with patch(
            "app.api.v1.products.products.get_current_store_id",
            new=AsyncMock(return_value=(1001, 2001)),
        ), patch(
            "app.api.v1.products.products.inventory_controller.get_balance_data",
            new=AsyncMock(return_value=(1, mock_rows)),
        ):
            response = await list_product(page=1, page_size=10, name="")
        payload = json.loads(response.body)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["data"][0]["name"], "可乐")

    async def test_inventory_warning_response_shape(self):
        mock_rows = [{"id": 1, "name": "牛奶", "is_low_stock": True}]
        with patch(
            "app.api.v1.inventories.inventories.get_current_store_id",
            new=AsyncMock(return_value=2001),
        ), patch(
            "app.api.v1.inventories.inventories.inventory_controller.get_warning_data",
            new=AsyncMock(return_value=(1, mock_rows)),
        ):
            response = await get_inventory_warning_list(page=1, page_size=10)
        payload = json.loads(response.body)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["total"], 1)
        self.assertTrue(payload["data"][0]["is_low_stock"])

    async def test_finance_overview_response_shape(self):
        mock_data = {
            "sale_amount": 320.0,
            "return_amount": 20.0,
            "net_sales_amount": 300.0,
            "net_sales_qty": 8,
            "txn_count": 4,
        }
        with patch(
            "app.api.v1.finances.finances.get_current_store_id",
            new=AsyncMock(return_value=2001),
        ), patch(
            "app.api.v1.finances.finances.finance_controller.get_overview",
            new=AsyncMock(return_value=mock_data),
        ):
            response = await get_finance_overview()
        payload = json.loads(response.body)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["net_sales_amount"], 300.0)
        self.assertEqual(payload["data"]["txn_count"], 4)

    async def test_finance_statement_response_shape(self):
        mock_rows = [{"date": "2026-04-03", "net_sales_amount": 520.0, "net_sales_qty": 16}]
        with patch(
            "app.api.v1.finances.finances.get_current_store_id",
            new=AsyncMock(return_value=2001),
        ), patch(
            "app.api.v1.finances.finances.finance_controller.get_statement_data",
            new=AsyncMock(return_value=(1, mock_rows)),
        ):
            response = await get_finance_statement_list(page=1, page_size=10)
        payload = json.loads(response.body)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["data"][0]["date"], "2026-04-03")
