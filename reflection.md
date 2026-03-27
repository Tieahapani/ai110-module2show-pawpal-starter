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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
