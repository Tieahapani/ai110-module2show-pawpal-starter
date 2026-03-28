import streamlit as st
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    Priority, TaskType, TimePreference,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — persists data across Streamlit reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------
st.header("1. Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Minutes available for pet care today",
        min_value=10, max_value=480, value=120, step=10,
    )
    submitted = st.form_submit_button("Save Owner")
    if submitted:
        st.session_state.owner = Owner(
            name=owner_name,
            available_minutes=int(available_minutes),
        )
        st.success(f"Owner saved: {owner_name} ({available_minutes} min available)")

if st.session_state.owner is None:
    st.info("Fill in your name and available time above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2: Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.header("2. Your Pets")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    add_pet = st.form_submit_button("Add Pet")
    if add_pet:
        new_pet = Pet(name=pet_name, species=species, age=int(age))
        owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Current pets:**")
    for pet in owner.pets:
        st.markdown(f"- **{pet.name}** ({pet.species}, age {pet.age}) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets added yet.")

# ---------------------------------------------------------------------------
# Section 3: Add a task
# ---------------------------------------------------------------------------
st.divider()
st.header("3. Add a Care Task")

if not owner.pets:
    st.warning("Add at least one pet before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)

        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            task_type = st.selectbox("Task type", [t.value for t in TaskType])
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        with col2:
            priority = st.selectbox("Priority", [p.value for p in Priority], index=2)
            time_pref = st.selectbox("Time preference", [t.value for t in TimePreference])

        add_task = st.form_submit_button("Add Task")
        if add_task:
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(Task(
                title=task_title,
                task_type=TaskType(task_type),
                duration_minutes=int(duration),
                priority=Priority(priority),
                time_preference=TimePreference(time_pref),
            ))
            st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Show all tasks per pet
    all_pairs = owner.get_all_tasks()
    if all_pairs:
        st.write("**All tasks:**")
        rows = [
            {
                "Pet": pet.name,
                "Task": task.title,
                "Type": task.task_type.value,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority.value,
                "Time Pref": task.time_preference.value,
            }
            for pet, task in all_pairs
        ]
        st.table(rows)

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Generate Today's Schedule")

if not owner.get_all_tasks():
    st.warning("Add tasks before generating a schedule.")
else:
    if st.button("Generate Schedule", type="primary"):
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        conflicts = scheduler.detect_conflicts()
        time_warnings = scheduler.detect_time_conflicts()

        # --- Time conflict warnings ---
        if time_warnings:
            for w in time_warnings:
                st.warning(w)

        # --- Sorted daily plan ---
        st.subheader("Daily Plan")
        if plan:
            sorted_plan = scheduler.sort_by_time(plan)
            plan_rows = [
                {
                    "Start": item.start_time,
                    "Pet": item.pet.name,
                    "Task": item.task.title,
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority.value,
                    "Reason": item.reason,
                }
                for item in sorted_plan
            ]
            st.table(plan_rows)

            total = sum(s.task.duration_minutes for s in plan)
            st.success(
                f"Scheduled **{len(plan)} tasks** using **{total} of "
                f"{owner.available_minutes} minutes**."
            )
        else:
            st.warning("No tasks could be scheduled within your available time.")

        # --- Budget conflicts ---
        if conflicts:
            st.subheader("Could Not Fit")
            st.caption("These tasks were skipped because the time budget ran out:")
            for t in conflicts:
                st.markdown(f"- **{t.title}** ({t.duration_minutes} min, {t.priority.value} priority)")

        # --- Filter panel ---
        st.divider()
        st.subheader("Filter Tasks")
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox(
                "Filter by pet", ["All"] + [p.name for p in owner.pets]
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by status", ["All", "Incomplete", "Completed"]
            )

        pet_name_arg = None if pet_filter == "All" else pet_filter
        completed_arg = None if status_filter == "All" else (status_filter == "Completed")
        filtered = scheduler.filter_tasks(pet_name=pet_name_arg, completed=completed_arg)

        if filtered:
            st.table([
                {
                    "Pet": p.name,
                    "Task": t.title,
                    "Priority": t.priority.value,
                    "Done": "✓" if t.completed else "○",
                }
                for p, t in filtered
            ])
        else:
            st.info("No tasks match the selected filters.")
