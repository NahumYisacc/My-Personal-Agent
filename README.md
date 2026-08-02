# Progress Tracker Agent

A simple command-line agent for organizing classes, goals, and study progress.

## Features
- Add new goals or classes to track
- Update progress as a percentage
- Mark tasks as not started, in progress, or completed
- Review a quick summary of your workload

## Usage

```bash
python -m progress_agent.cli add "Study math" "Review chapter 3"
python -m progress_agent.cli list
python -m progress_agent.cli update <goal_id> 40
python -m progress_agent.cli complete <goal_id>
python -m progress_agent.cli summary
python -m progress_agent.cli seed-degree
```

### Degree and transfer tracking
Use the degree-seeding command to create a simple academic plan based on your transcript summary:

```bash
python -m progress_agent.cli seed-degree
python -m progress_agent.cli list
```
