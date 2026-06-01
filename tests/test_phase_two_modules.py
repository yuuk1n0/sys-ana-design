from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PhaseTwoModuleScaffoldTests(unittest.TestCase):
    def test_phase_two_view_files_exist(self):
        expected_files = [
            "web/src/views/store/member/index.vue",
            "web/src/views/store/store-employee/index.vue",
            "web/src/views/store/supplier/index.vue",
            "web/src/views/store/sales/index.vue",
            "web/src/views/system/user/index.vue",
            "web/src/views/system/role/index.vue",
            "web/src/views/system/menu/index.vue",
            "web/src/views/system/api/index.vue",
            "web/src/views/system/dept/index.vue",
            "web/src/views/system/auditlog/index.vue",
        ]
        for relative_path in expected_files:
            with self.subTest(file=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).exists(), f"缺少模块页面: {relative_path}")

    def test_store_menu_seed_contains_phase_two_entries(self):
        content = (PROJECT_ROOT / "app/core/init_app.py").read_text(encoding="utf-8")
        expected_entries = [
            'name="会员管理"',
            'component="/store/member"',
            'name="门店员工"',
            'component="/store/store-employee"',
            'name="供应商管理"',
            'component="/store/supplier"',
            'name="销售管理"',
            'component="/store/sales"',
            'name="系统管理"',
            'component="/system/user"',
            'component="/system/role"',
            'component="/system/menu"',
            'component="/system/api"',
            'component="/system/dept"',
            'component="/system/auditlog"',
        ]
        for item in expected_entries:
            with self.subTest(entry=item):
                self.assertIn(item, content)

    def test_frontend_api_helpers_cover_phase_two_modules(self):
        content = (PROJECT_ROOT / "web/src/api/index.js").read_text(encoding="utf-8")
        expected_helpers = [
            "getMemberList",
            "createMember",
            "updateMember",
            "deleteMember",
            "getStoreEmployeeList",
            "createStoreEmployee",
            "updateStoreEmployee",
            "deleteStoreEmployee",
            "getSupplierList",
            "createSupplier",
            "updateSupplier",
            "deleteSupplier",
            "getFinanceOverview",
            "getFinanceStatementList",
            "getUserList",
            "getRoleList",
            "getMenus",
            "getApis",
            "getDepts",
            "getAuditLogList",
        ]
        for helper in expected_helpers:
            with self.subTest(helper=helper):
                self.assertIn(helper, content)
