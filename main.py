"""
PawPal+ CLI demo.
Run with: python main.py
Verifies that Owner, Pet, Task, and Scheduler all work together.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TaskType, TimePreference


def main():
    # --- Setup owner ---
    owner = Owner(name="Jordan", available_minutes=120)

    # --- Setup pets ---
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Add tasks to Mochi (dog) ---
    mochi.add_task(Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
    ))
    mochi.add_task(Task(
        title="Breakfast feeding",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
    ))
    mochi.add_task(Task(
        title="Flea medication",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=Priority.HIGH,
        time_preference=TimePreference.ANYTIME,
    ))
    mochi.add_task(Task(
        title="Afternoon play",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        time_preference=TimePreference.AFTERNOON,
    ))
    mochi.add_task(Task(
        title="Bath & grooming",
        task_type=TaskType.GROOMING,
        duration_minutes=45,
        priority=Priority.LOW,
        time_preference=TimePreference.AFTERNOON,
    ))

    # --- Add tasks to Luna (cat) ---
    luna.add_task(Task(
        title="Breakfast feeding",
        task_type=TaskType.FEEDING,
        duration_minutes=5,
        priority=Priority.HIGH,
        time_preference=TimePreference.MORNING,
    ))
    luna.add_task(Task(
        title="Litter box cleaning",
        task_type=TaskType.OTHER,
        duration_minutes=10,
        priority=Priority.MEDIUM,
        time_preference=TimePreference.ANYTIME,
    ))
    luna.add_task(Task(
        title="Evening cuddle time",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=15,
        priority=Priority.LOW,
        time_preference=TimePreference.EVENING,
    ))

    # --- Run scheduler ---
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    # --- Print results ---
    print("\n" + scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
