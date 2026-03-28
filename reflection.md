# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Four classes were designed based on the core user actions: adding a pet, managing tasks, and generating a daily schedule.

- **Task** — holds what needs to happen (title, type, duration, priority, time preference). Uses Python dataclass for clean attribute declaration. Responsible only for describing a single care action.
- **Pet** — holds pet info (name, species, age) and owns a list of Tasks. Responsible for managing tasks assigned to that pet.
- **Owner** — holds owner info (name) and daily available time budget (in minutes). Owns a list of Pets. Provides a helper to collect all tasks across all pets.
- **Scheduler** — takes an Owner and generates a prioritized daily plan. Responsible for sorting tasks (high → medium → low), fitting them within the time budget, detecting conflicts (tasks that don't fit), and explaining the plan.

A `ScheduledTask` dataclass was also added as a result type — it wraps a Task with a start time and a reasoning string so the UI can display both the plan and the rationale.

**b. Design changes**

Yes — two notable changes from the original UML:

1. **`ScheduledTask` was added** as a fifth class not in the original UML. During implementation it became clear that `generate_plan()` needed to return more than just a list of `Task` objects — it needed to attach a start time and a reasoning string to each scheduled item. A separate result type kept `Task` clean and single-purpose.

2. **`get_all_tasks()` returns `(Pet, Task)` pairs instead of just `Task` objects.** The original UML had it returning `list[Task]`, but the Scheduler needs to know which pet each task belongs to in order to populate `ScheduledTask.pet`. Changing the return type to `list[tuple[Pet, Task]]` was the simplest fix without restructuring the classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: task priority (high/medium/low), the owner's daily time budget (available_minutes), and the owner's soft time-of-day preferences (morning/afternoon/evening/anytime). Priority was chosen as the primary constraint because missing a high-priority task like medication is more harmful than missing a low-priority grooming session. Time budget is the hard limit — no task is scheduled if it would exceed it. Time preference is a tiebreaker used to order tasks of equal priority rather than a hard deadline.

**b. Tradeoffs**

The scheduler uses a greedy algorithm — it sorts all tasks by priority and time preference, then accepts each one in order as long as it fits within the remaining time budget. This means a single long low-priority task at the end of the list can be skipped even if its duration would have fit had a shorter medium-priority task been dropped earlier. This is a reasonable tradeoff for a daily pet care scenario: owners generally want the most important tasks done first rather than an optimal packing of the schedule, and the greedy approach is simple enough to reason about and explain to the user.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used throughout every phase of this project. In Phase 1, it helped brainstorm the four-class architecture and generate the Mermaid.js UML diagram from a plain-English description of the problem. In Phase 2, it scaffolded the class skeletons using Python dataclasses and helped implement the greedy scheduling algorithm. In Phases 3 and 4, it helped identify that `st.session_state` was needed to prevent Streamlit from resetting the Owner on every rerun, and it suggested the sorted sweep approach for conflict detection. The most useful prompts were specific ones tied to a concrete file or method — for example, asking "how should the Scheduler retrieve all tasks from Owner's pets given this skeleton?" produced a much better answer than a vague open-ended question.

**b. Judgment and verification**

The initial conflict detection implementation used a nested loop (O(n²)) that checked every pair of tasks. The AI suggested keeping it for readability since the task count is small. We rejected that suggestion and replaced it with a sorted sweep (O(n log n)) with an early `break` — both more efficient AND still readable because the `break` makes the algorithm's intent explicit. The change was verified by running the existing test suite (all 27 tests passed) and checking that the conflict warning output in `main.py` remained correct.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers 27 cases across: Task priority values and `mark_complete()` behavior; daily and weekly recurrence generating the correct next due date using `timedelta`; Pet task addition and removal; Owner task aggregation across multiple pets; Scheduler plan generation respecting the time budget and priority ordering; `sort_by_time()` returning chronological order; `filter_tasks()` filtering by pet name and completion status; `detect_time_conflicts()` correctly flagging overlapping `requested_start` windows and ignoring tasks without one; and edge cases including a pet with no tasks, a single task longer than the entire budget, and zero available minutes.

These tests matter because the scheduler's core promise — "most important tasks first, within your time" — is easy to break silently. A bug in priority sorting or time budget calculation would produce a wrong schedule with no obvious error message, so automated tests are the only reliable way to catch regressions.

**b. Confidence**

Confidence level: ★★★★☆. The backend logic is thoroughly tested and all 27 tests pass. The main gap is end-to-end UI testing — Streamlit interactions cannot be verified by pytest without a browser automation tool like Playwright or Selenium, which is out of scope for this project. Edge cases that would be worth testing next: tasks with identical priority and duration (checking stable sort order), an owner with 10+ pets each with 20+ tasks (performance at scale), and recurring tasks across a month boundary (e.g., marking complete on March 31st).

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the most valuable part of the process. Building and verifying `pawpal_system.py` through `main.py` before touching `app.py` meant that when the Streamlit integration was written, it worked on the first try. Every bug was caught at the backend level where it was easy to debug, not buried inside a UI callback. The `_build_plan()` refactor — extracting a shared private method so the scheduling algorithm only runs once — was also satisfying because it made the code both faster and cleaner at the same time.

**b. What you would improve**

The `requested_start` field on Task is optional, which means conflict detection only works for tasks where the owner explicitly sets a preferred time. A better design would use the scheduler-assigned start times to detect conflicts automatically, so all tasks are checked without any extra input from the user. Additionally, the recurring task feature currently requires the caller to manually call `pet.add_task(next_task)` after `mark_complete()` — this could be handled automatically inside the Scheduler to reduce friction.

**c. Key takeaway**

The most important lesson was that AI works best as a collaborator at the design and implementation level, not as a replacement for human judgment about tradeoffs. The AI could generate code quickly, but every significant decision — which algorithm to use, what the return type of `get_all_tasks()` should be, whether to optimize for readability or performance — required stopping, evaluating the suggestion in context, and sometimes pushing back. Being the "lead architect" meant owning those decisions, using AI to accelerate execution, and verifying every output rather than accepting it as correct.
