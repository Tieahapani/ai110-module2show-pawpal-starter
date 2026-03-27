"""
PawPal+ backend logic.
All scheduling classes live here. app.py imports from this module.
"""

from dataclasses import dataclass, field
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

    def priority_value(self) -> int:
        """Return a numeric value for sorting; higher means more important."""
        mapping = {Priority.LOW: 1, Priority.MEDIUM: 2, Priority.HIGH: 3}
        return mapping[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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

    def generate_plan(self) -> list[ScheduledTask]:
        """Return an ordered list of ScheduledTasks that fit within the time budget."""
        plan: list[ScheduledTask] = []
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
                minutes_used += task.duration_minutes

        return plan

    def detect_conflicts(self) -> list[Task]:
        """Return tasks that could not be scheduled due to time constraints."""
        scheduled_tasks = {id(st.task) for st in self.generate_plan()}
        return [task for _, task in self.owner.get_all_tasks() if id(task) not in scheduled_tasks]

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Return a human-readable summary of the generated plan."""
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

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append(f"\nCould not fit {len(conflicts)} task(s):")
            for t in conflicts:
                lines.append(f"  - {t.title} ({t.duration_minutes} min, {t.priority.value})")

        return "\n".join(lines)
