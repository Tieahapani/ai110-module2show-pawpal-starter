# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes several algorithms that make the scheduler more intelligent:

- **Priority-based sorting** — tasks are sorted high → medium → low before scheduling. Within the same priority level, tasks with a time-of-day preference (morning/afternoon/evening) are scheduled before open-ended tasks.
- **Greedy time-budget allocation** — the scheduler fits as many tasks as possible within the owner's available minutes, always starting with the highest-priority tasks first.
- **Conflict detection (time budget)** — tasks that cannot fit within the remaining time budget are flagged and reported separately rather than silently dropped.
- **Time conflict detection** — if two tasks have overlapping `requested_start` windows, a warning is returned. Uses a sorted sweep algorithm (O(n log n)) for efficiency instead of checking every pair (O(n²)).
- **Filtering** — tasks can be filtered by pet name or completion status using `Scheduler.filter_tasks()`.
- **Recurring tasks** — tasks marked as `daily` or `weekly` automatically generate the next occurrence when `mark_complete()` is called, using Python's `timedelta`.
