"""
PawPal+ backend logic.
All scheduling classes live here. app.py imports from this module.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimePreference(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANYTIME = "anytime"


class TaskType(str, Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    VET = "vet"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Core data classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care task."""
    title: str
    task_type: TaskType
    duration_minutes: int
    priority: Priority
    time_preference: TimePreference = TimePreference.ANYTIME
    completed: bool = False
    frequency: str = "none"          # "none" | "daily" | "weekly"
    due_date: Optional[date] = None  # date this task is due
    requested_start: Optional[str] = None  # owner's preferred start "HH:MM"

    def priority_value(self) -> int:
        """Return a numeric value for sorting; higher means more important."""
        mapping = {Priority.LOW: 1, Priority.MEDIUM: 2, Priority.HIGH: 3}
        return mapping[self.priority]

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete; return next occurrence if recurring, else None."""
        self.completed = True
        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time_preference=self.time_preference,
            frequency=self.frequency,
            due_date=next_due,
            requested_start=self.requested_start,
        )


@dataclass
class Pet:
    """Represents a pet owned by an Owner."""
    name: str
    species: str  # "dog", "cat", or "other"
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list. Raises ValueError if not found."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """Represents the pet owner and their daily time budget."""
    name: str
    available_minutes: int  # total minutes available for pet care today
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple["Pet", Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """A Task that has been placed into the daily plan."""
    task: Task
    pet: Pet
    start_time: Optional[str] = None  # e.g. "08:00" — assigned by Scheduler
    reason: str = ""                  # why this task was included


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

def _minutes_to_time(base_hour: int, base_minute: int, offset: int) -> str:
    """Convert a base time plus an offset in minutes to an HH:MM string."""
    total = base_hour * 60 + base_minute + offset
    return f"{total // 60:02d}:{total % 60:02d}"


def _time_pref_order(pref: TimePreference) -> int:
    """Return sort key for time preference (lower = earlier in day)."""
    return {
        TimePreference.MORNING: 0,
        TimePreference.AFTERNOON: 1,
        TimePreference.EVENING: 2,
        TimePreference.ANYTIME: 3,
    }[pref]


class Scheduler:
    """
    Generates a daily care plan for all pets belonging to an owner.

    Strategy:
      1. Collect all (pet, task) pairs from all pets.
      2. Sort by priority descending, then by time_preference ascending.
      3. Greedily add tasks until the owner's available_minutes budget is exhausted.
      4. Tasks that don't fit are returned as conflicts.
    """

    DAY_START_HOUR = 8   # schedule starts at 08:00

    def __init__(self, owner: Owner):
        self.owner = owner

    def _sorted_pairs(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs sorted by priority then time preference."""
        pairs = self.owner.get_all_tasks()
        return sorted(
            pairs,
            key=lambda pt: (-pt[1].priority_value(), _time_pref_order(pt[1].time_preference)),
        )

    def _build_plan(self) -> tuple[list[ScheduledTask], list[Task]]:
        """Run the scheduling algorithm once; return (plan, unscheduled_conflicts)."""
        plan: list[ScheduledTask] = []
        scheduled_ids: set[int] = set()
        minutes_used = 0

        for pet, task in self._sorted_pairs():
            if minutes_used + task.duration_minutes <= self.owner.available_minutes:
                start = _minutes_to_time(self.DAY_START_HOUR, 0, minutes_used)
                plan.append(ScheduledTask(
                    task=task,
                    pet=pet,
                    start_time=start,
                    reason=f"Priority: {task.priority.value}",
                ))
                scheduled_ids.add(id(task))
                minutes_used += task.duration_minutes

        conflicts = [task for _, task in self.owner.get_all_tasks() if id(task) not in scheduled_ids]
        return plan, conflicts

    def generate_plan(self) -> list[ScheduledTask]:
        """Return an ordered list of ScheduledTasks that fit within the time budget."""
        return self._build_plan()[0]

    def detect_conflicts(self) -> list[Task]:
        """Return tasks that could not be scheduled due to time constraints."""
        return self._build_plan()[1]

    def sort_by_time(self, plan: list[ScheduledTask]) -> list[ScheduledTask]:
        """Return the plan sorted by start_time (HH:MM) ascending."""
        return sorted(plan, key=lambda item: item.start_time or "99:99")

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs filtered by pet name and/or completion status."""
        results = self.owner.get_all_tasks()
        if pet_name is not None:
            results = [(p, t) for p, t in results if p.name == pet_name]
        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]
        return results

    def detect_time_conflicts(self) -> list[str]:
        """Return warning strings for tasks whose requested_start windows overlap.

        Uses a sorted sweep (O(n log n)) instead of pairwise comparison (O(n²)):
        after sorting by start time, each task only needs to be checked against
        subsequent tasks until one starts after the current task ends.
        """
        def to_minutes(hhmm: str) -> int:
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m

        # Build and sort windows by start time — O(n log n)
        windows = sorted(
            [
                (to_minutes(t.requested_start), to_minutes(t.requested_start) + t.duration_minutes, t.title, p.name)
                for p, t in self.owner.get_all_tasks()
                if t.requested_start is not None
            ],
            key=lambda w: w[0],
        )

        warnings: list[str] = []
        for i, (_, e1, title1, pet1) in enumerate(windows):
            for s2, _, title2, pet2 in windows[i + 1:]:
                if s2 >= e1:
                    break  # sorted by start — no further overlaps possible
                warnings.append(
                    f"⚠ Time conflict: '{title1}' ({pet1}) and '{title2}' ({pet2}) "
                    f"overlap at their requested times."
                )
        return warnings

    def explain_plan(self, plan: Optional[list[ScheduledTask]] = None) -> str:
        """Return a human-readable summary of the generated plan."""
        if plan is None:
            plan, conflicts = self._build_plan()
        else:
            conflicts = self._build_plan()[1]

        if not plan:
            return "No tasks could be scheduled within the available time."

        lines = [f"Daily Plan for {self.owner.name} ({self.owner.available_minutes} min available)",
                 "-" * 55]

        minutes_used = 0
        for st in plan:
            lines.append(
                f"{st.start_time}  {st.pet.name:<10} {st.task.title:<22} "
                f"({st.task.duration_minutes} min, {st.task.priority.value})"
            )
            minutes_used += st.task.duration_minutes

        lines.append("-" * 55)
        lines.append(f"Scheduled {len(plan)} tasks using {minutes_used} of "
                     f"{self.owner.available_minutes} available minutes.")

        if conflicts:
            lines.append(f"\nCould not fit {len(conflicts)} task(s):")
            for t in conflicts:
                lines.append(f"  - {t.title} ({t.duration_minutes} min, {t.priority.value})")

        return "\n".join(lines)
