"""
pytest test suite for PawPal+ core logic.
Run with: python -m pytest

Covers:
  - Task: priority values, mark_complete, recurring recurrence
  - Pet: add/remove tasks
  - Owner: add pets, aggregate tasks
  - Scheduler: plan generation, time budget, priority ordering,
    sort_by_time, filter_tasks, detect_time_conflicts
"""

import pytest
from datetime import date, timedelta
from pawpal_system import (
    Owner, Pet, Task, Scheduler, ScheduledTask,
    Priority, TaskType, TimePreference,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    return Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
    )


@pytest.fixture
def sample_pet():
    return Pet(name="Mochi", species="dog", age=3)


@pytest.fixture
def sample_owner():
    return Owner(name="Jordan", available_minutes=120)


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(sample_task):
    """Calling mark_complete() should set completed to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True


def test_priority_value_ordering():
    """HIGH > MEDIUM > LOW in priority_value()."""
    low = Task("a", TaskType.OTHER, 10, Priority.LOW)
    med = Task("b", TaskType.OTHER, 10, Priority.MEDIUM)
    high = Task("c", TaskType.OTHER, 10, Priority.HIGH)
    assert low.priority_value() < med.priority_value() < high.priority_value()


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count(sample_pet, sample_task):
    """Adding a task to a Pet should increase its task count by 1."""
    assert len(sample_pet.tasks) == 0
    sample_pet.add_task(sample_task)
    assert len(sample_pet.tasks) == 1


def test_remove_task_decreases_count(sample_pet, sample_task):
    """Removing a task from a Pet should decrease its task count."""
    sample_pet.add_task(sample_task)
    sample_pet.remove_task(sample_task)
    assert len(sample_pet.tasks) == 0


def test_remove_task_not_present_raises(sample_pet, sample_task):
    """Removing a task that was never added should raise ValueError."""
    with pytest.raises(ValueError):
        sample_pet.remove_task(sample_task)


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_add_pet_increases_count(sample_owner, sample_pet):
    """Adding a pet to an Owner should increase the pet count."""
    assert len(sample_owner.pets) == 0
    sample_owner.add_pet(sample_pet)
    assert len(sample_owner.pets) == 1


def test_get_all_tasks_aggregates_across_pets(sample_owner):
    """get_all_tasks should return tasks from all pets."""
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk", TaskType.WALK, 30, Priority.HIGH))
    cat.add_task(Task("Feed", TaskType.FEEDING, 10, Priority.HIGH))
    sample_owner.add_pet(dog)
    sample_owner.add_pet(cat)
    assert len(sample_owner.get_all_tasks()) == 2


def test_get_all_tasks_empty_when_no_pets(sample_owner):
    """get_all_tasks returns empty list when owner has no pets."""
    assert sample_owner.get_all_tasks() == []


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_generate_plan_respects_time_budget():
    """Tasks that exceed the time budget should not appear in the plan."""
    owner = Owner(name="Test", available_minutes=30)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Long walk", TaskType.WALK, 25, Priority.HIGH))
    pet.add_task(Task("Feeding", TaskType.FEEDING, 10, Priority.HIGH))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    total = sum(st.task.duration_minutes for st in plan)
    assert total <= 30


def test_generate_plan_orders_by_priority():
    """Higher priority tasks should appear before lower priority tasks."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Low task", TaskType.OTHER, 10, Priority.LOW))
    pet.add_task(Task("High task", TaskType.OTHER, 10, Priority.HIGH))
    pet.add_task(Task("Med task", TaskType.OTHER, 10, Priority.MEDIUM))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    priorities = [st.task.priority_value() for st in plan]
    assert priorities == sorted(priorities, reverse=True)


def test_generate_plan_empty_when_no_time():
    """With zero available minutes, plan should be empty."""
    owner = Owner(name="Test", available_minutes=0)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Walk", TaskType.WALK, 30, Priority.HIGH))
    owner.add_pet(pet)

    assert Scheduler(owner).generate_plan() == []


def test_detect_conflicts_returns_unscheduled():
    """Tasks that don't fit should appear in conflicts."""
    owner = Owner(name="Test", available_minutes=20)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Short task", TaskType.OTHER, 15, Priority.HIGH))
    pet.add_task(Task("Long task", TaskType.OTHER, 60, Priority.MEDIUM))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert any(t.title == "Long task" for t in conflicts)


def test_explain_plan_no_tasks_message():
    """explain_plan on an empty plan should return a graceful message."""
    owner = Owner(name="Test", available_minutes=0)
    result = Scheduler(owner).explain_plan([])
    assert "No tasks" in result


def test_start_times_are_sequential():
    """Start times should advance correctly as tasks are added."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Task A", TaskType.OTHER, 30, Priority.HIGH))
    pet.add_task(Task("Task B", TaskType.OTHER, 45, Priority.HIGH))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert plan[0].start_time == "08:00"
    assert plan[1].start_time == "08:30"


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return ScheduledTasks ordered by start_time ascending."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    # Add in reverse priority so scheduler assigns later start times first
    pet.add_task(Task("Low task",  TaskType.OTHER, 10, Priority.LOW))
    pet.add_task(Task("High task", TaskType.OTHER, 10, Priority.HIGH))
    pet.add_task(Task("Med task",  TaskType.OTHER, 10, Priority.MEDIUM))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    sorted_plan = scheduler.sort_by_time(plan)
    times = [item.start_time for item in sorted_plan]
    assert times == sorted(times)


def test_sort_by_time_single_task():
    """sort_by_time() on a one-item plan should return that same item."""
    owner = Owner(name="Test", available_minutes=60)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Walk", TaskType.WALK, 30, Priority.HIGH))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert scheduler.sort_by_time(plan) == plan


# ---------------------------------------------------------------------------
# Recurring task tests
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day():
    """mark_complete() on a daily task should return a task due tomorrow."""
    today = date.today()
    task = Task(
        title="Feeding",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
        frequency="daily",
        due_date=today,
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.title == task.title


def test_weekly_recurrence_creates_next_week():
    """mark_complete() on a weekly task should return a task due in 7 days."""
    today = date.today()
    task = Task(
        title="Bath",
        task_type=TaskType.GROOMING,
        duration_minutes=45,
        priority=Priority.LOW,
        frequency="weekly",
        due_date=today,
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_non_recurring_task_returns_none_on_complete():
    """mark_complete() on a non-recurring task should return None."""
    task = Task("Walk", TaskType.WALK, 30, Priority.HIGH, frequency="none")
    assert task.mark_complete() is None


def test_recurring_task_is_marked_complete():
    """mark_complete() should set completed=True on the original task."""
    task = Task("Feeding", TaskType.FEEDING, 10, Priority.HIGH, frequency="daily")
    task.mark_complete()
    assert task.completed is True


# ---------------------------------------------------------------------------
# Time conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_time_conflicts_flags_overlap():
    """Two tasks with overlapping requested_start windows should produce a warning."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    # Walk: 08:00–08:30, Feeding: 08:15–08:25 — overlap
    pet.add_task(Task("Walk",    TaskType.WALK,    30, Priority.HIGH, requested_start="08:00"))
    pet.add_task(Task("Feeding", TaskType.FEEDING, 10, Priority.HIGH, requested_start="08:15"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_time_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_detect_time_conflicts_no_overlap():
    """Tasks with non-overlapping requested_start windows should produce no warnings."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    # Walk: 08:00–08:30, Feeding: 09:00–09:10 — no overlap
    pet.add_task(Task("Walk",    TaskType.WALK,    30, Priority.HIGH, requested_start="08:00"))
    pet.add_task(Task("Feeding", TaskType.FEEDING, 10, Priority.HIGH, requested_start="09:00"))
    owner.add_pet(pet)

    assert Scheduler(owner).detect_time_conflicts() == []


def test_detect_time_conflicts_ignores_tasks_without_requested_start():
    """Tasks without a requested_start should not be checked for conflicts."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Walk",    TaskType.WALK,    30, Priority.HIGH))  # no requested_start
    pet.add_task(Task("Feeding", TaskType.FEEDING, 10, Priority.HIGH))  # no requested_start
    owner.add_pet(pet)

    assert Scheduler(owner).detect_time_conflicts() == []


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    owner = Owner(name="Test", available_minutes=120)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk", TaskType.WALK, 30, Priority.HIGH))
    cat.add_task(Task("Feed", TaskType.FEEDING, 10, Priority.HIGH))
    owner.add_pet(dog)
    owner.add_pet(cat)

    results = Scheduler(owner).filter_tasks(pet_name="Mochi")
    assert len(results) == 1
    assert results[0][1].title == "Walk"


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=True) should return only completed tasks."""
    owner = Owner(name="Test", available_minutes=120)
    pet = Pet("Rex", "dog", 2)
    t1 = Task("Walk", TaskType.WALK, 30, Priority.HIGH)
    t2 = Task("Feed", TaskType.FEEDING, 10, Priority.HIGH)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)

    done = Scheduler(owner).filter_tasks(completed=True)
    pending = Scheduler(owner).filter_tasks(completed=False)
    assert len(done) == 1
    assert len(pending) == 1


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_does_not_affect_plan():
    """A pet with no tasks should not cause errors or affect the plan."""
    owner = Owner(name="Test", available_minutes=60)
    empty_pet = Pet("Ghost", "cat", 1)
    active_pet = Pet("Rex", "dog", 2)
    active_pet.add_task(Task("Walk", TaskType.WALK, 20, Priority.HIGH))
    owner.add_pet(empty_pet)
    owner.add_pet(active_pet)

    plan = Scheduler(owner).generate_plan()
    assert len(plan) == 1
    assert plan[0].task.title == "Walk"


def test_single_task_longer_than_budget_goes_to_conflicts():
    """A single task longer than available_minutes should appear in conflicts."""
    owner = Owner(name="Test", available_minutes=10)
    pet = Pet("Rex", "dog", 2)
    pet.add_task(Task("Long walk", TaskType.WALK, 60, Priority.HIGH))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []
    assert len(scheduler.detect_conflicts()) == 1
