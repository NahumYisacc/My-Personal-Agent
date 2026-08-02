from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class ProgressTracker:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path or "data/progress.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = {"goals": []}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    self._data = data
        self._data.setdefault("goals", [])

    def _save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, indent=2)

    @staticmethod
    def _calculate_progress(completed_units: int | float | None, target_units: int | float | None) -> int:
        if target_units in (None, 0):
            return 0
        if completed_units is None:
            completed_units = 0
        return max(0, min(100, int(round((float(completed_units) / float(target_units)) * 100))))

    def add_goal(
        self,
        title: str,
        notes: str = "",
        category: str = "general",
        target_units: int | float | None = None,
        completed_units: int | float | None = None,
    ) -> str:
        goal_id = str(uuid.uuid4())[:8]
        progress = 0
        status = "not_started"

        if target_units is not None:
            progress = self._calculate_progress(completed_units, target_units)
            if progress == 100:
                status = "completed"
            elif progress > 0:
                status = "in_progress"

        goal = {
            "id": goal_id,
            "title": title,
            "notes": notes,
            "status": status,
            "progress": progress,
            "category": category,
            "target_units": target_units,
            "completed_units": completed_units,
        }
        self._data.setdefault("goals", []).append(goal)
        self._save()
        return goal_id

    def get_goal(self, goal_id: str) -> dict[str, Any]:
        for goal in self._data.get("goals", []):
            if goal.get("id") == goal_id:
                return goal
        raise KeyError(f"Goal {goal_id} not found")

    def list_goals(self) -> list[dict[str, Any]]:
        return list(self._data.get("goals", []))

    def update_progress(self, goal_id: str, progress: int) -> None:
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
        goal = self.get_goal(goal_id)
        goal["progress"] = progress
        if progress == 100:
            goal["status"] = "completed"
        elif progress > 0:
            goal["status"] = "in_progress"
        self._save()

    def mark_status(self, goal_id: str, status: str) -> None:
        valid_statuses = {"not_started", "in_progress", "completed", "blocked"}
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {sorted(valid_statuses)}")
        goal = self.get_goal(goal_id)
        goal["status"] = status
        if status == "completed":
            goal["progress"] = 100
        elif status == "not_started":
            goal["progress"] = 0
        self._save()

    def seed_degree_plan(self) -> list[str]:
        milestones = [
            (
                "SMC AA degree progress",
                "Based on your unofficial transcript: 51 completed units toward the AA pathway.",
                "degree",
                60,
                51,
            ),
            (
                "CSU transfer progress",
                "Track your CSU transfer completion using the transcript totals.",
                "transfer",
                60,
                51,
            ),
            (
                "UC transfer progress",
                "Track your UC transfer completion using the transcript totals.",
                "transfer",
                48,
                42,
            ),
            (
                "TTU transfer planning",
                "Next steps: application materials, transcripts, and transfer evaluation.",
                "transfer",
                100,
                25,
            ),
        ]
        return [
            self.add_goal(title, notes, category=category, target_units=target_units, completed_units=completed_units)
            for title, notes, category, target_units, completed_units in milestones
        ]

    def summary(self) -> dict[str, int]:
        goals = self.list_goals()
        return {
            "total": len(goals),
            "not_started": sum(1 for item in goals if item.get("status") == "not_started"),
            "in_progress": sum(1 for item in goals if item.get("status") == "in_progress"),
            "completed": sum(1 for item in goals if item.get("status") == "completed"),
            "blocked": sum(1 for item in goals if item.get("status") == "blocked"),
        }
