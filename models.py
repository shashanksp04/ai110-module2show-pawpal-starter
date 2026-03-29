from __future__ import annotations

from dataclasses import dataclass
from typing import List


class Owner:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Pet:
    def __init__(self, name: str, species: str) -> None:
        self._name = name
        self._species = species

    @property
    def name(self) -> str:
        return self._name

    @property
    def species(self) -> str:
        return self._species


class Task:
    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
    ) -> None:
        self._title = title
        self._duration_minutes = duration_minutes
        self._priority = priority

    @property
    def title(self) -> str:
        return self._title

    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes

    @property
    def priority(self) -> str:
        return self._priority


class DailyPlan:
    @dataclass(frozen=True)
    class PlanSlot:
        order: int
        task: Task
        explanation: str

        def get_order(self) -> int:
            return self.order

        def get_task(self) -> Task:
            return self.task

        def get_explanation(self) -> str:
            return self.explanation

    def __init__(self, pet: Pet, slots: List[DailyPlan.PlanSlot]) -> None:
        self._pet = pet
        self._slots = list(slots)

    @property
    def pet(self) -> Pet:
        return self._pet

    @property
    def slots(self) -> List[DailyPlan.PlanSlot]:
        return list(self._slots)


class Scheduler:
    def __init__(self) -> None:
        pass

    def build_plan(self, owner: Owner, pet: Pet, tasks: List[Task]) -> DailyPlan:
        return DailyPlan(pet, [])
