from __future__ import annotations

from dataclasses import dataclass


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        description: str,
        time_minutes: int,
        frequency: str,
        completed: bool = False,
    ) -> None:
        """Create a task with description, duration, frequency, and completion flag."""
        self._description = description
        self._time_minutes = time_minutes
        self._frequency = frequency.strip().lower()
        self._completed = completed

    @property
    def description(self) -> str:
        """Return the task description."""
        return self._description

    @property
    def time_minutes(self) -> int:
        """Return how long the task takes in minutes."""
        return self._time_minutes

    @property
    def frequency(self) -> str:
        """Return how often the task should happen (e.g. daily, weekly)."""
        return self._frequency

    @property
    def completed(self) -> bool:
        """Return whether the task is marked done."""
        return self._completed

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self._completed = True


class Pet:
    """A pet and the tasks that belong to it."""

    def __init__(self, name: str, species: str) -> None:
        """Create a pet with a name, species, and an empty task list."""
        self._name = name
        self._species = species
        self._tasks: list[Task] = []

    @property
    def name(self) -> str:
        """Return the pet's name."""
        return self._name

    @property
    def species(self) -> str:
        """Return the pet's species."""
        return self._species

    @property
    def tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's tasks."""
        return list(self._tasks)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's list."""
        self._tasks.append(task)


class Owner:
    """An owner who has one or more pets."""

    def __init__(self, name: str) -> None:
        """Create an owner with a name and no pets yet."""
        self._name = name
        self._pets: list[Pet] = []

    @property
    def name(self) -> str:
        """Return the owner's name."""
        return self._name

    @property
    def pets(self) -> list[Pet]:
        """Return a shallow copy of this owner's pets."""
        return list(self._pets)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self._pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task from every pet (order follows pet order, then task order)."""
        out: list[Task] = []
        for pet in self._pets:
            out.extend(pet.tasks)
        return out


class DailyPlan:
    """An ordered schedule for one run of the scheduler."""

    @dataclass(frozen=True)
    class PlanSlot:
        """One row in the schedule: pet, task, order, and explanation."""

        order: int
        pet: Pet
        task: Task
        explanation: str

        def get_order(self) -> int:
            """Return the step number in today's schedule."""
            return self.order

        def get_pet(self) -> Pet:
            """Return the pet this slot belongs to."""
            return self.pet

        def get_task(self) -> Task:
            """Return the scheduled task."""
            return self.task

        def get_explanation(self) -> str:
            """Return why this task was placed here."""
            return self.explanation

    def __init__(self, slots: list[PlanSlot]) -> None:
        """Build a plan from an ordered list of slots."""
        self._slots = list(slots)

    @property
    def slots(self) -> list[DailyPlan.PlanSlot]:
        """Return a copy of the schedule slots."""
        return list(self._slots)


class Scheduler:
    """Collects tasks from an owner's pets and builds an ordered daily plan."""

    _FREQUENCY_RANK: dict[str, int] = {"daily": 3, "weekly": 2, "once": 1}

    def __init__(self) -> None:
        """Create a scheduler with no internal state."""
        pass

    def build_plan(self, owner: Owner) -> DailyPlan:
        """Gather incomplete tasks from all pets, sort them, and attach explanations."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in owner.pets:
            for task in pet.tasks:
                if not task.completed:
                    pairs.append((pet, task))

        if not pairs:
            return DailyPlan([])

        ordered = sorted(
            pairs,
            key=lambda pt: (
                -self._frequency_rank(pt[1].frequency),
                pt[1].time_minutes,
                pt[0].name.lower(),
                pt[1].description.lower(),
            ),
        )

        slots: list[DailyPlan.PlanSlot] = []
        for index, (pet, task) in enumerate(ordered, start=1):
            explanation = self._explain_slot(
                index, owner, pet, task, ordered, len(ordered)
            )
            slots.append(DailyPlan.PlanSlot(index, pet, task, explanation))
        return DailyPlan(slots)

    def _frequency_rank(self, frequency: str) -> int:
        """Map a frequency label to a sortable rank (higher = earlier in the day)."""
        return self._FREQUENCY_RANK.get(frequency.strip().lower(), 0)

    def _explain_slot(
        self,
        order: int,
        owner: Owner,
        pet: Pet,
        task: Task,
        ordered_pairs: list[tuple[Pet, Task]],
        total: int,
    ) -> str:
        """Build a short human-readable reason for this slot."""
        label = task.frequency.capitalize()
        duration = task.time_minutes
        prev = ordered_pairs[order - 2] if order > 1 else None

        base = (
            f'Step {order}/{total}: "{task.description}" ({duration} min, {label}) '
            f"for {pet.name} ({pet.species})."
        )
        if order == 1:
            reason = (
                "Scheduled first: highest recurring importance among pending tasks "
                "(ties: shorter time first, then pet name, then description)."
            )
        else:
            assert prev is not None
            prev_pet, prev_task = prev
            r = self._frequency_rank(task.frequency)
            r_prev = self._frequency_rank(prev_task.frequency)
            if r == r_prev and pet is prev_pet:
                reason = (
                    "Same frequency and pet as the previous step; shorter tasks are listed first."
                )
            elif r == r_prev:
                reason = (
                    "Same frequency tier; ordered by time, then pet name, to balance care across pets."
                )
            else:
                reason = (
                    "Lower frequency tier than earlier steps, so it comes after more recurring care."
                )

        return f"{base} {reason} Planned for {owner.name}."
