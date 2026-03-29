"""Temporary demo script to exercise pawpal_system in the terminal."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Alex")

    mochi = Pet("Mochi", "dog")
    neko = Pet("Neko", "cat")

    mochi.add_task(Task("Morning walk", 30, "daily"))
    mochi.add_task(Task("Heart medication", 5, "daily"))
    neko.add_task(Task("Litter check", 10, "weekly"))

    owner.add_pet(mochi)
    owner.add_pet(neko)

    plan = Scheduler().build_plan(owner)

    print("Today's Schedule")
    print("=" * 60)
    if not plan.slots:
        print("(No pending tasks.)")
        return

    for slot in plan.slots:
        t = slot.get_task()
        p = slot.get_pet()
        print(f"\n{slot.get_order()}. {p.name} ({p.species}) — {t.description}")
        print(f"   Time: {t.time_minutes} min  |  Frequency: {t.frequency}  |  Done: {t.completed}")
        print(f"   Note: {slot.get_explanation()}")


if __name__ == "__main__":
    main()
