"""PawPal+ logic layer.

Class stubs generated from diagrams/uml_draft.mmd. No scheduling logic yet —
attributes and method signatures only.
"""

import uuid
from dataclasses import dataclass, field, fields
from typing import List, Optional

VALID_PRIORITIES = {"low", "medium", "high"}


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    pet_name: str
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self) -> None:
        self.priority = self.priority.lower()
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")

    def priority_score(self) -> int:
        pass

    def __str__(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates) -> None:
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"no task with task_id {task_id!r} for pet {self.name!r}")

        valid_fields = {f.name for f in fields(Task)}
        unknown = set(updates) - valid_fields
        if unknown:
            raise AttributeError(f"Task has no field(s): {sorted(unknown)}")

        for key, value in updates.items():
            setattr(task, key, value)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def list_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time: int = 0

    def add_pet(self, pet: Pet) -> None:
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"a pet named {pet.name!r} already exists for this owner")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, tasks: List[Task], available_time: int, start_time: str):
        self.tasks = tasks
        self.available_time = available_time
        self.start_time = start_time
        self.scheduled_items: List = []
        self.skipped_tasks: List[Task] = []

    @classmethod
    def from_owner(cls, owner: Owner, start_time: str) -> "Scheduler":
        return cls(owner.get_all_tasks(), owner.available_time, start_time)

    def sort_tasks(self) -> None:
        pass

    def filter_tasks(self) -> None:
        pass

    def generate_plan(self) -> None:
        """Should call self.sort_tasks() then self.filter_tasks() before
        building scheduled_items, so sorting always happens before filtering."""
        pass

    def explain(self) -> str:
        pass

    def display_plan(self) -> str:
        pass
