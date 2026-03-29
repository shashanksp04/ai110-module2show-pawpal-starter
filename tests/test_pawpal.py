"""Tests for pawpal_system.Task, Pet, Owner, DailyPlan, and Scheduler."""

from pawpal_system import DailyPlan, Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status() -> None:
    task = Task("Brush fur", 15, "daily", completed=False)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 20, "daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", 5, "daily"))
    assert len(pet.tasks) == 2


# --- Pressure / stress ---


def test_many_tasks_single_pet_orders_by_frequency_then_time() -> None:
    pet = Pet("Stress", "dog")
    for i in range(120):
        pet.add_task(Task(f"task-{i:03d}", time_minutes=(i % 60) + 1, frequency="once"))
    pet.add_task(Task("daily-short", 1, "daily"))
    pet.add_task(Task("weekly-mid", 30, "weekly"))

    owner = Owner("O")
    owner.add_pet(pet)
    plan = Scheduler().build_plan(owner)

    assert len(plan.slots) == 122
    first = plan.slots[0].get_task()
    assert first.description == "daily-short"
    assert first.frequency == "daily"
    # All slot orders unique and sequential
    orders = [s.get_order() for s in plan.slots]
    assert orders == list(range(1, 123))


def test_many_pets_many_tasks_all_included() -> None:
    owner = Owner("Multi")
    n_pets = 25
    tasks_per = 8
    for p in range(n_pets):
        pet = Pet(f"Pet{p}", "cat" if p % 2 else "dog")
        for t in range(tasks_per):
            pet.add_task(Task(f"P{p}-T{t}", 5 + t, "daily"))
        owner.add_pet(pet)

    plan = Scheduler().build_plan(owner)
    assert len(plan.slots) == n_pets * tasks_per
    seen = {(s.get_pet().name, s.get_task().description) for s in plan.slots}
    assert len(seen) == n_pets * tasks_per


def test_owner_all_tasks_matches_flattened_count() -> None:
    owner = Owner("Alex")
    for i in range(15):
        p = Pet(f"P{i}", "other")
        for j in range(20):
            p.add_task(Task(f"job-{i}-{j}", 10, "weekly"))
        owner.add_pet(p)
    assert len(owner.all_tasks()) == 15 * 20


def test_scheduler_ignores_completed_tasks_only() -> None:
    pet = Pet("Mochi", "dog")
    for i in range(50):
        t = Task(f"open-{i}", 10, "daily")
        if i % 3 == 0:
            t.mark_complete()
        pet.add_task(t)
    owner = Owner("O")
    owner.add_pet(pet)
    plan = Scheduler().build_plan(owner)
    expected_pending = sum(1 for i in range(50) if i % 3 != 0)
    assert len(plan.slots) == expected_pending
    assert all(not s.get_task().completed for s in plan.slots)


def test_all_tasks_completed_yields_empty_plan() -> None:
    pet = Pet("X", "cat")
    for i in range(100):
        t = Task(f"t{i}", 1, "daily")
        t.mark_complete()
        pet.add_task(t)
    owner = Owner("O")
    owner.add_pet(pet)
    assert Scheduler().build_plan(owner).slots == []


def test_daily_plan_slots_copy_is_isolated() -> None:
    pet = Pet("P", "dog")
    pet.add_task(Task("a", 1, "daily"))
    owner = Owner("O")
    owner.add_pet(pet)
    plan = Scheduler().build_plan(owner)
    slots = plan.slots
    slots.append(plan.slots[0])
    assert len(plan.slots) == 1


def test_pet_tasks_copy_is_isolated() -> None:
    pet = Pet("P", "dog")
    pet.add_task(Task("a", 1, "daily"))
    tasks = pet.tasks
    tasks.append(Task("b", 2, "once"))
    assert len(pet.tasks) == 1


def test_unknown_frequency_sorts_after_once() -> None:
    pet = Pet("P", "dog")
    pet.add_task(Task("once", 1, "once"))
    pet.add_task(Task("weird", 1, "adhoc"))
    owner = Owner("O")
    owner.add_pet(pet)
    plan = Scheduler().build_plan(owner)
    titles = [s.get_task().description for s in plan.slots]
    assert titles[0] == "once"
    assert titles[1] == "weird"


def test_scheduler_stable_under_repeated_builds() -> None:
    owner = Owner("O")
    p = Pet("M", "dog")
    for i in range(30):
        p.add_task(Task(f"x{i}", (i * 7) % 120 + 1, ["daily", "weekly", "once"][i % 3]))
    owner.add_pet(p)
    s = Scheduler()
    a = [s.get_task().description for s in s.build_plan(owner).slots]
    b = [s.get_task().description for s in s.build_plan(owner).slots]
    assert a == b


def test_high_volume_plan_under_one_second() -> None:
    import time

    owner = Owner("Bench")
    p = Pet("Big", "dog")
    for i in range(2000):
        p.add_task(Task(f"t{i}", 1 + (i % 90), "daily"))
    owner.add_pet(p)
    t0 = time.perf_counter()
    plan = Scheduler().build_plan(owner)
    elapsed = time.perf_counter() - t0
    assert len(plan.slots) == 2000
    assert elapsed < 1.0, f"build_plan took {elapsed:.2f}s"
