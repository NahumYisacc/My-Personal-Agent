from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class ProgressTracker:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path or "data/progress.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = {"goals": [], "courses": []}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    self._data = data
        self._data.setdefault("goals", [])
        self._data.setdefault("courses", [])

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

    @staticmethod
    def _grade_to_points(grade: str | None) -> float | None:
        if grade is None:
            return None
        normalized = str(grade).strip().upper()
        if normalized in {"", "N/A", "NA", "NONE"}:
            return None
        if normalized in {"A", "A+"}:
            return 4.0
        if normalized == "A-":
            return 3.7
        if normalized == "B+":
            return 3.3
        if normalized == "B":
            return 3.0
        if normalized == "B-":
            return 2.7
        if normalized == "C+":
            return 2.3
        if normalized == "C":
            return 2.0
        if normalized == "C-":
            return 1.7
        if normalized == "D+":
            return 1.3
        if normalized == "D":
            return 1.0
        if normalized in {"F", "NP", "NO PASS", "NC", "NO CREDIT"}:
            return 0.0
        if normalized in {"P", "PASS", "CR", "CREDIT"}:
            return None
        try:
            value = float(normalized)
        except ValueError:
            return None
        return value if 0.0 <= value <= 4.0 else None

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

    def add_course(self, title: str, units: int | float, grade: str | None = None) -> str:
        try:
            unit_count = int(units)
        except (TypeError, ValueError) as exc:
            raise ValueError("Units must be an integer") from exc
        if unit_count <= 0:
            raise ValueError("Units must be greater than 0")

        course_id = str(uuid.uuid4())[:8]
        course = {
            "id": course_id,
            "title": title,
            "units": unit_count,
            "grade": grade,
            "grade_points": self._grade_to_points(grade),
        }
        self._data.setdefault("courses", []).append(course)
        self._save()
        return course_id

    def add_class(self, title: str, units: int | float, grade: str | None = None) -> str:
        return self.add_course(title, units, grade)

    def get_course(self, course_id: str) -> dict[str, Any]:
        for course in self._data.get("courses", []):
            if course.get("id") == course_id:
                return course
        raise KeyError(f"Course {course_id} not found")

    def list_courses(self) -> list[dict[str, Any]]:
        return list(self._data.get("courses", []))

    def get_course_summary(self) -> dict[str, Any]:
        courses = self.list_courses()
        total_units = sum(int(course.get("units", 0) or 0) for course in courses)
        graded_units = sum(int(course.get("units", 0) or 0) for course in courses if course.get("grade_points") is not None)
        weighted_points = sum(
            (float(course.get("grade_points") or 0.0) * int(course.get("units", 0) or 0))
            for course in courses
            if course.get("grade_points") is not None
        )
        gpa = round(weighted_points / graded_units, 2) if graded_units else 0.0
        return {
            "total_courses": len(courses),
            "total_units": total_units,
            "graded_units": graded_units,
            "gpa": gpa,
        }

    def seed_degree_plan(self) -> list[str]:
        existing_goals = list(self._data.get("goals", []))
        self._data["goals"] = [
            goal
            for goal in existing_goals
            if not any(
                goal.get("title", "").startswith(prefix)
                for prefix in (
                    "SMC AA degree progress",
                    "CSU transfer progress",
                    "TTU transfer progress",
                    "UC transfer progress",
                    "TTU transfer planning",
                )
            )
        ]

        milestones = [
            (
                "SMC AA degree progress",
                "Based on your unofficial transcript: 51 completed units toward the AA pathway.",
                "degree",
                60,
                51,
            ),
            (
                "TTU transfer progress",
                "Track your TTU transfer completion using the transcript totals.",
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
        goal_ids = []
        for milestone in milestones:
            goal_ids.append(self.add_goal(milestone[0], milestone[1], category=milestone[2], target_units=milestone[3], completed_units=milestone[4]))
        return goal_ids

    def summary(self) -> dict[str, int]:
        goals = self.list_goals()
        return {
            "total": len(goals),
            "not_started": sum(1 for item in goals if item.get("status") == "not_started"),
            "in_progress": sum(1 for item in goals if item.get("status") == "in_progress"),
            "completed": sum(1 for item in goals if item.get("status") == "completed"),
            "blocked": sum(1 for item in goals if item.get("status") == "blocked"),
        }
