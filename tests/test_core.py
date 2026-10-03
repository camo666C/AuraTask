import unittest
import os
import tempfile
from src.models import Task
from src.storage import TaskStorage
from src.icons import IconManager
from src.glass_theme import GlassColors, apply_windows_acrylic


class TestTaskModel(unittest.TestCase):
    def test_task_creation_and_defaults(self):
        t = Task(title="Сдать курсач")
        self.assertEqual(t.title, "Сдать курсач")
        self.assertFalse(t.completed)
        self.assertEqual(t.priority, "medium")
        self.assertEqual(t.category, "Общее")
        self.assertTrue(len(t.id) > 0)

    def test_serialization_roundtrip(self):
        t1 = Task(title="Подготовить отчет", priority="high", category="Учеба")
        data = t1.to_dict()
        t2 = Task.from_dict(data)
        self.assertEqual(t1.id, t2.id)
        self.assertEqual(t1.title, t2.title)
        self.assertEqual(t1.priority, t2.priority)
        self.assertEqual(t1.category, t2.category)
        self.assertEqual(t1.completed, t2.completed)


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "tasks_test.json")
        self.storage = TaskStorage(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        bak = f"{self.db_path}.bak"
        if os.path.exists(bak):
            os.remove(bak)
        if os.path.exists(self.tmp_dir):
            os.rmdir(self.tmp_dir)

    def test_save_and_load(self):
        tasks = [
            Task(title="Задача 1", priority="high"),
            Task(title="Задача 2", completed=True, priority="low")
        ]
        ok = self.storage.save_tasks(tasks)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(self.db_path))

        loaded = self.storage.load_tasks()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].title, "Задача 1")
        self.assertEqual(loaded[0].priority, "high")
        self.assertTrue(loaded[1].completed)

    def test_corrupted_json_recovery(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write("{невалидный json content")

        loaded = self.storage.load_tasks()
        self.assertEqual(loaded, [])
        self.assertTrue(os.path.exists(f"{self.db_path}.bak"))


class TestIcons(unittest.TestCase):
    def test_icons_generation(self):
        icons = ["plus", "trash", "check", "search", "filter", "refresh", "clear", "unknown"]
        for icon_name in icons:
            icon = IconManager.get_icon(icon_name, size=16, color="#0EA5E9")
            self.assertIsNotNone(icon)

    def test_app_icon_pil(self):
        pil_img = IconManager.get_app_icon_pil(48)
        self.assertEqual(pil_img.size, (48, 48))


class TestTheme(unittest.TestCase):
    def test_colors_presence(self):
        self.assertTrue(GlassColors.BG_WINDOW.startswith("#"))
        self.assertTrue(GlassColors.ACCENT_CYAN.startswith("#"))

    def test_apply_windows_acrylic_safe_on_linux(self):
        # Должен отрабатывать без падений на любой платформе
        apply_windows_acrylic(None)


if __name__ == "__main__":
    unittest.main()
