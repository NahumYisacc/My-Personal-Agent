import tempfile
import unittest
from pathlib import Path

from progress_agent.tracker import ProgressTracker


class ProgressTrackerTests(unittest.TestCase):
    def test_add_update_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir) / "progress.json"
            tracker = ProgressTracker(storage_path)

            goal_id = tracker.add_goal("Study algebra", "Practice equations")
            self.assertEqual(tracker.get_goal(goal_id)["title"], "Study algebra")

            tracker.update_progress(goal_id, 40)
            self.assertEqual(tracker.get_goal(goal_id)["progress"], 40)

            tracker.mark_status(goal_id, "in_progress")
            self.assertEqual(tracker.get_goal(goal_id)["status"], "in_progress")

            summary = tracker.summary()
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["in_progress"], 1)

    def test_seed_degree_plan_creates_milestones(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir) / "progress.json"
            tracker = ProgressTracker(storage_path)

            goal_ids = tracker.seed_degree_plan()
            self.assertEqual(len(goal_ids), 4)

            aa_goal = tracker.get_goal(goal_ids[0])
            self.assertEqual(aa_goal["category"], "degree")
            self.assertEqual(aa_goal["target_units"], 60)
            self.assertEqual(aa_goal["completed_units"], 51)
            self.assertEqual(aa_goal["progress"], 85)

    def test_seed_degree_plan_replaces_stale_transfer_goals(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir) / "progress.json"
            tracker = ProgressTracker(storage_path)
            tracker.add_goal("CSU transfer progress", "Old plan")
            tracker.seed_degree_plan()

            goals = tracker.list_goals()
            self.assertEqual(len(goals), 4)
            self.assertTrue(all("CSU" not in goal["title"] for goal in goals))
            self.assertTrue(any("TTU transfer progress" == goal["title"] for goal in goals))


if __name__ == "__main__":
    unittest.main()
