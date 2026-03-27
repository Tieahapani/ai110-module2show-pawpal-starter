"""
PawPal+ CLI demo.
Run with: python3 main.py
Demonstrates: scheduling, sorting, filtering, recurring tasks, conflict detection.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TaskType, TimePreference


def section(title: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print('=' * 55)


def main():
    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    owner = Owner(name="Jordan", available_minutes=120)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks added intentionally out of priority order to demo sorting
    mochi.add_task(Task(
        title="Afternoon play",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        time_preference=TimePreference.AFTERNOON,
        requested_start="13:00",
    ))
    mochi.add_task(Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
        requested_start="08:00",
    ))
    mochi.add_task(Task(
        title="Flea medication",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=Priority.HIGH,
        time_preference=TimePreference.ANYTIME,
    ))
    mochi.add_task(Task(
        title="Bath & grooming",
        task_type=TaskType.GROOMING,
        duration_minutes=45,
        priority=Priority.LOW,
        time_preference=TimePreference.AFTERNOON,
    ))

    luna.add_task(Task(
        title="Breakfast feeding",
        task_type=TaskType.FEEDING,
        duration_minutes=5,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
        frequency="daily",
        due_date=date.today(),
        requested_start="08:15",   # overlaps Mochi's walk → conflict!
    ))
    luna.add_task(Task(
        title="Litter box cleaning",
        task_type=TaskType.OTHER,
        duration_minutes=10,
        priority=Priority.MEDIUM,
        time_preference=TimePreference.ANYTIME,
    ))

    scheduler = Scheduler(owner)

    # ------------------------------------------------------------------
    # 1. Generate and display the daily plan
    # ------------------------------------------------------------------
    section("1. DAILY SCHEDULE")
    plan = scheduler.generate_plan()
    print(scheduler.explain_plan(plan))

    # ------------------------------------------------------------------
    # 2. Sort plan by start time (HH:MM)
    # ------------------------------------------------------------------
    section("2. PLAN SORTED BY START TIME")
    sorted_plan = scheduler.sort_by_time(plan)
    for item in sorted_plan:
        print(f"  {item.start_time}  {item.pet.name:<10} {item.task.title}")

    # ------------------------------------------------------------------
    # 3. Filter tasks — by pet name and by completion status
    # ------------------------------------------------------------------
    section("3. FILTER: Mochi's tasks only")
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    for pet, task in mochi_tasks:
        status = "✓" if task.completed else "○"
        print(f"  [{status}] {task.title} ({task.priority.value})")

    section("3. FILTER: Incomplete tasks across all pets")
    incomplete = scheduler.filter_tasks(completed=False)
    for pet, task in incomplete:
        print(f"  {pet.name:<10} {task.title}")

    # ------------------------------------------------------------------
    # 4. Conflict detection — two tasks with overlapping requested_start
    # ------------------------------------------------------------------
    section("4. CONFLICT DETECTION")
    conflicts = scheduler.detect_time_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No time conflicts detected.")

    # ------------------------------------------------------------------
    # 5. Recurring tasks — mark complete and get next occurrence
    # ------------------------------------------------------------------
    section("5. RECURRING TASK — mark complete and reschedule")
    feeding = luna.tasks[0]  # "Breakfast feeding" — daily
    print(f"  Before: '{feeding.title}' due {feeding.due_date}, completed={feeding.completed}")
    next_task = feeding.mark_complete()
    print(f"  After:  completed={feeding.completed}")
    if next_task:
        print(f"  Next occurrence created: '{next_task.title}' due {next_task.due_date}")
        luna.add_task(next_task)

    section("5b. FILTER: Completed tasks (after marking feeding done)")
    done = scheduler.filter_tasks(completed=True)
    for pet, task in done:
        print(f"  ✓ {pet.name:<10} {task.title}")


if __name__ == "__main__":
    main()
