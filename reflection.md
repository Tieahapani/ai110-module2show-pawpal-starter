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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
