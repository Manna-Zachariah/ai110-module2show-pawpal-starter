import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

# The Owner lives in st.session_state so it survives Streamlit's top-to-bottom
# rerun on every interaction, instead of being recreated (and emptied) each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

st.markdown("### Pets")
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

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(Task(name=task_title, duration=int(duration), priority=priority, pet_name=pet.name))

if pet.list_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {"title": t.name, "duration_minutes": t.duration, "priority": t.priority}
            for t in pet.list_tasks()
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
sched_col1, sched_col2 = st.columns(2)
with sched_col1:
    available_time = st.number_input("Available time today (minutes)", min_value=0, max_value=600, value=60)
with sched_col2:
    start_time = st.text_input("Start time (HH:MM)", value="09:00")

if st.button("Generate schedule"):
    owner.available_time = int(available_time)
    scheduler = Scheduler.from_owner(owner, start_time)
    scheduler.generate_plan()
    st.markdown("**Plan:**")
    st.text(scheduler.display_plan())
    st.markdown("**Explanation:**")
    st.write(scheduler.explain())
