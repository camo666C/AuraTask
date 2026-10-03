import json
import os
import shutil
import tempfile
from typing import List
from .models import Task


class TaskStorage:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename

    def load_tasks(self) -> List[Task]:
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return [Task.from_dict(item) for item in data if isinstance(item, dict)]
        except (json.JSONDecodeError, OSError):
            backup_path = f"{self.filename}.bak"
            if os.path.exists(self.filename):
                try:
                    shutil.copy2(self.filename, backup_path)
                except OSError:
                    pass
            return []

    def save_tasks(self, tasks: List[Task]) -> bool:
        data = [task.to_dict() for task in tasks]
        dir_name = os.path.dirname(os.path.abspath(self.filename)) or "."

        # Атомарная запись через временный файл в той же директории
        tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix="tasks_tmp_", suffix=".json")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.filename)
            return True
        except OSError:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return False
