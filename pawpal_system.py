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

    def priority_value(self) -> int:
        """Return a numeric value for sorting (higher = more important)."""
        pass  # TODO: implement


@dataclass
class Pet:
    """Represents a pet owned by an Owner."""
    name: str
    species: str  # "dog", "cat", or "other"
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass  # TODO: implement

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass  # TODO: implement


@dataclass
class Owner:
    """Represents the pet owner and their daily time budget."""
    name: str
    available_minutes: int  # total minutes available for pet care today
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        pass  # TODO: implement

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        pass  # TODO: implement


@dataclass
class ScheduledTask:
    """A Task that has been placed into the daily plan."""
    task: Task
    pet: Pet
    start_time: Optional[str] = None  # e.g. "08:00" — set by Scheduler
    reason: str = ""                  # explanation of why this task was included


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Generates a daily care plan for all pets belonging to an owner.

    Strategy:
      1. Collect all tasks from all pets.
      2. Sort by priority (high → medium → low), then by time_preference.
      3. Greedily add tasks until the owner's available_minutes budget is exhausted.
      4. Flag conflicts (tasks that didn't fit).
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> list[ScheduledTask]:
        """Return an ordered list of ScheduledTasks that fit within the time budget."""
        pass  # TODO: implement

    def detect_conflicts(self) -> list[Task]:
        """Return tasks that could not be scheduled due to time constraints."""
        pass  # TODO: implement

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Return a human-readable summary of the generated plan."""
        pass  # TODO: implement
