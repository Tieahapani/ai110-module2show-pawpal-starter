"""
pytest test suite for PawPal+ core logic.
Run with: python -m pytest
"""

import pytest
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
