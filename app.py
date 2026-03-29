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
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_desc = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Time (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0)

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "description": task_desc,
            "time_minutes": int(duration),
            "frequency": frequency,
        }
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(owner_name)
        pet = Pet(pet_name, species)
        for row in st.session_state.tasks:
            pet.add_task(
                Task(
                    description=row["description"],
                    time_minutes=int(row["time_minutes"]),
                    frequency=row["frequency"],
                )
            )
        owner.add_pet(pet)
        plan = Scheduler().build_plan(owner)

        st.success(f"Schedule for **{owner.name}** — **{pet.name}** ({pet.species})")
        rows = []
        for slot in plan.slots:
            t = slot.get_task()
            p = slot.get_pet()
            rows.append(
                {
                    "Order": slot.get_order(),
                    "Pet": p.name,
                    "Task": t.description,
                    "Minutes": t.time_minutes,
                    "Frequency": t.frequency,
                    "Done": t.completed,
                    "Why": slot.get_explanation(),
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
