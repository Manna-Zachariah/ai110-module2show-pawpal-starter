from datetime import datetime, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart daily care planner for pet owners.")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences — and
warns them when two tasks are scheduled at the same time.
"""
    )

st.divider()

st.subheader("Owner & Pets")
owner_name = st.text_input("Owner name", value="Jordan")

# The Owner lives in st.session_state so it survives Streamlit's top-to-bottom
# rerun on every interaction, instead of being recreated (and emptied) each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    st.write("")
    if st.button("Add pet"):
        try:
            owner.add_pet(Pet(name=new_pet_name, species=species))
        except ValueError as exc:
            st.error(str(exc))

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_name = st.selectbox("Choose pet", [p.name for p in owner.pets])
pet = owner.get_pet(pet_name)

st.divider()

st.subheader("Tasks")
st.caption("Give a task a preferred time to enable conflict detection, and a recurrence to have it repeat automatically.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    preferred_time_raw = st.text_input("Preferred time (HH:MM, optional)", value="")
with col5:
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
with col6:
    st.write("")
    if st.button("Add task"):
        preferred_time = preferred_time_raw.strip() or None
        try:
            if preferred_time is not None:
                datetime.strptime(preferred_time, "%H:%M")
            pet.add_task(
                Task(
                    name=task_title,
                    duration=int(duration),
                    priority=priority,
                    pet_name=pet.name,
                    preferred_time=preferred_time,
                    recurrence=recurrence,
                )
            )
        except ValueError:
            st.error("Preferred time must be in HH:MM format (e.g. 08:00), and priority/recurrence must be valid.")

if pet.list_tasks():
    st.write(f"Current tasks for {pet.name}:")
    st.table(
        [
            {
                "Task": t.name,
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Time": t.preferred_time or "—",
                "Recurrence": t.recurrence,
                "Status": "✅ Done" if t.is_complete else "⏳ Pending",
            }
            for t in pet.list_tasks()
        ]
    )

    with st.expander("Manage tasks"):
        for t in pet.list_tasks():
            row1, row2, row3 = st.columns([3, 1, 1])
            row1.write(str(t))
            if row2.button("✅ Complete", key=f"complete-{t.task_id}"):
                next_task = pet.complete_task(t.task_id)
                if next_task is not None:
                    st.success(f"Nice work! Next occurrence of '{next_task.name}' is due {next_task.occurrence_date}.")
                st.rerun()
            if row3.button("🗑️ Remove", key=f"remove-{t.task_id}"):
                pet.remove_task(t.task_id)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# Live conflict check across every pet, since one owner can't be in two places
# at once even if the conflicting tasks belong to different pets.
all_tasks = owner.get_all_tasks()
live_conflicts = Scheduler(all_tasks, owner.available_time, start_time="00:00").get_conflict_warnings() if all_tasks else []
if live_conflicts:
    st.warning(f"⚠️ **{len(live_conflicts)} scheduling conflict(s) found across your pets:**")
    for warning in live_conflicts:
        st.warning(warning)

st.subheader("Build Today's Plan")
sched_col1, sched_col2 = st.columns(2)
with sched_col1:
    available_time = st.number_input("Available time today (minutes)", min_value=0, max_value=600, value=60)
with sched_col2:
    start_time = st.text_input("Start time (HH:MM)", value="09:00")

sort_mode = st.radio("Order tasks by", ["Priority (recommended)", "Time of day"], horizontal=True)

if st.button("Generate schedule", type="primary"):
    owner.available_time = int(available_time)
    scheduler = Scheduler.from_owner(owner, start_time)

    conflicts = scheduler.get_conflict_warnings()
    if conflicts:
        st.error(f"⚠️ {len(conflicts)} conflict(s) below need attention before you rely on this plan:")
        for warning in conflicts:
            st.warning(warning)

    if sort_mode.startswith("Priority"):
        scheduler.generate_plan()
    else:
        scheduler.sort_by_time()
        scheduler.filter_tasks()
        current_time = datetime.strptime(scheduler.start_time, "%H:%M")
        scheduler.scheduled_items = []
        for task in scheduler.tasks:
            scheduler.scheduled_items.append((current_time.strftime("%H:%M"), task))
            current_time += timedelta(minutes=task.duration)

    if scheduler.scheduled_items:
        st.markdown("**📋 Today's Plan**")
        st.table(
            [
                {
                    "Time": time,
                    "Task": task.name,
                    "Pet": task.pet_name,
                    "Priority": task.priority,
                    "Duration (min)": task.duration,
                }
                for time, task in scheduler.scheduled_items
            ]
        )
    else:
        st.info("No tasks scheduled.")

    if scheduler.skipped_tasks:
        st.warning(
            "⏭️ Skipped due to insufficient available time: "
            + ", ".join(f"'{t.name}' ({t.pet_name})" for t in scheduler.skipped_tasks)
        )

    if not conflicts and not scheduler.skipped_tasks and scheduler.scheduled_items:
        st.success("✅ Full plan generated with no conflicts — you're all set!")

    with st.expander("Why this plan?"):
        st.write(scheduler.explain())
