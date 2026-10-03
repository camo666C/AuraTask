from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid


@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    category: str = "Общее"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            title=data.get("title", ""),
            completed=bool(data.get("completed", False)),
            priority=data.get("priority", "medium"),
            category=data.get("category", "Общее"),
            created_at=data.get("created_at", datetime.now().strftime("%d.%m.%Y %H:%M")),
            description=data.get("description", "")
        )
