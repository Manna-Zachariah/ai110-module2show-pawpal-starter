"""PawPal+ logic layer.

Class stubs generated from diagrams/uml_draft.mmd. No scheduling logic yet —
attributes and method signatures only.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    pet_name: str

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
        pass

    def edit_task(self, task_id: str, **updates) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def list_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time: int = 0

    def add_pet(self, pet: Pet) -> None:
        pass

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

    def sort_tasks(self) -> None:
        pass

    def filter_tasks(self) -> None:
        pass

    def generate_plan(self) -> None:
        pass

    def explain(self) -> str:
        pass

    def display_plan(self) -> str:
        pass
