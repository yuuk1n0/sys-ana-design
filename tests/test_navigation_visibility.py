from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NavigationVisibilityTests(unittest.TestCase):
    def test_seed_menu_removes_top_level_demo_entry(self):
        content = (PROJECT_ROOT / "app/core/init_app.py").read_text(encoding="utf-8")
        self.assertNotIn('name="一级菜单"', content)
        self.assertNotIn('path="/top-menu"', content)
        self.assertNotIn('component="/top-menu"', content)

    def test_error_page_group_is_hidden_in_frontend_routes(self):
        content = (PROJECT_ROOT / "web/src/router/routes/index.js").read_text(encoding="utf-8")
        self.assertIn("name: 'ErrorPage'", content)
        self.assertIn("isHidden: true", content)

    def test_top_menu_view_is_removed(self):
        self.assertFalse((PROJECT_ROOT / "web/src/views/top-menu/index.vue").exists())
