from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CourseDesignExtensionTests(unittest.TestCase):
    def test_course_design_overview_backend_and_frontend_are_registered(self):
        base_api = (PROJECT_ROOT / "app/api/v1/base/base.py").read_text(encoding="utf-8")
        frontend_api = (PROJECT_ROOT / "web/src/api/index.js").read_text(encoding="utf-8")

        self.assertIn("/course_design_overview", base_api)
        self.assertIn("getCourseDesignOverview", frontend_api)

    def test_new_course_design_pages_exist(self):
        expected_files = [
            "web/src/views/store/course-design/index.vue",
            "web/src/views/store/warehouse-center/index.vue",
            "web/src/views/store/finance-center/index.vue",
            "web/src/views/system/ops-center/index.vue",
        ]
        for relative_path in expected_files:
            with self.subTest(file=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).exists(), f"缺少课程设计页面: {relative_path}")

    def test_menu_seed_contains_course_design_entries(self):
        content = (PROJECT_ROOT / "app/core/init_app.py").read_text(encoding="utf-8")
        expected_entries = [
            'name="课程总览"',
            'component="/store/course-design"',
            'name="仓库中心"',
            'component="/store/warehouse-center"',
            'name="财务中心"',
            'component="/store/finance-center"',
            'name="运维中心"',
            'component="/system/ops-center"',
        ]
        for item in expected_entries:
            with self.subTest(entry=item):
                self.assertIn(item, content)
