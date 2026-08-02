from __future__ import annotations

import argparse
from pathlib import Path

from progress_agent.tracker import ProgressTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track your goals and progress")
    parser.add_argument("command", choices=["add", "list", "update", "status", "complete", "summary", "seed-degree"], help="Action to perform")
    parser.add_argument("value", nargs="?", help="Title, notes, goal id, or percentage")
    parser.add_argument("value2", nargs="?", help="Optional notes or status")
    parser.add_argument("--storage", default="data/progress.json", help="Path to the JSON storage file")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    tracker = ProgressTracker(Path(args.storage))

    if args.command == "add":
        title = args.value or "New goal"
        notes = args.value2 or ""
        goal_id = tracker.add_goal(title, notes)
        print(f"Added goal {goal_id}: {title}")
    elif args.command == "list":
        for goal in tracker.list_goals():
            line = f"{goal['id']} | {goal['title']} | {goal['status']} | {goal['progress']}%"
            if goal.get("target_units") is not None and goal.get("completed_units") is not None:
                line += f" | {goal['completed_units']}/{goal['target_units']} units"
            if goal.get("category"):
                line += f" | {goal['category']}"
            print(line)
    elif args.command == "update":
        goal_id = args.value
        progress = int(args.value2 or 0)
        tracker.update_progress(goal_id, progress)
        print(f"Updated {goal_id} to {progress}%")
    elif args.command == "status":
        goal_id = args.value
        status = args.value2 or "in_progress"
        tracker.mark_status(goal_id, status)
        print(f"Marked {goal_id} as {status}")
    elif args.command == "complete":
        goal_id = args.value
        tracker.mark_status(goal_id, "completed")
        print(f"Completed {goal_id}")
    elif args.command == "summary":
        summary = tracker.summary()
        print(summary)
    elif args.command == "seed-degree":
        goal_ids = tracker.seed_degree_plan()
        print(f"Added {len(goal_ids)} degree milestones")
        for goal_id in goal_ids:
            print(goal_id)


if __name__ == "__main__":
    main()
