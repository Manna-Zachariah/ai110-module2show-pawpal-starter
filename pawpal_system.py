"""PawPal+ logic layer.

Class stubs generated from diagrams/uml_draft.mmd. No scheduling logic yet —
attributes and method signatures only.
"""

import uuid
from dataclasses import dataclass, field, fields
from datetime import datetime, timedelta
from typing import List, Optional

VALID_PRIORITIES = {"low", "medium", "high"}


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    pet_name: str
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    is_complete: bool = False

    def __post_init__(self) -> None:
        """Normalize the priority string and validate it against VALID_PRIORITIES."""
        self.priority = self.priority.lower()
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")

    def priority_score(self) -> int:
        """Return a numeric weight for the task's priority (high=3, medium=2, low=1)."""
        return {"high": 3, "medium": 2, "low": 1}[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.is_complete = True

    def __str__(self) -> str:
        """Return a human-readable summary of the task."""
        return f"{self.name} ({self.duration} min) [priority: {self.priority}]"


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign the task to this pet and add it to its task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates) -> None:
        """Update the named fields on the task matching task_id."""
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
        """Remove the task matching task_id from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def list_tasks(self) -> List[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time: int = 0

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting duplicate pet names."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"a pet named {pet.name!r} already exists for this owner")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None if not found."""
        return next((p for p in self.pets if p.name == name), None)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, tasks: List[Task], available_time: int, start_time: str):
        self.tasks = tasks
        self.available_time = available_time
        self.start_time = start_time
        self.scheduled_items: List = []
        self.skipped_tasks: List[Task] = []

    @classmethod
    def from_owner(cls, owner: Owner, start_time: str) -> "Scheduler":
        """Build a Scheduler from an owner's tasks and available time."""
        return cls(owner.get_all_tasks(), owner.available_time, start_time)

    def sort_tasks(self) -> None:
        """Sort tasks by descending priority, then by shorter duration."""
        self.tasks.sort(key=lambda t: (-t.priority_score(), t.duration))

    def filter_tasks(self) -> None:
        """Keep only the tasks that fit within available_time, tracking the rest as skipped."""
        remaining_time = self.available_time
        fitted: List[Task] = []
        self.skipped_tasks = []
        for task in self.tasks:
            if task.duration <= remaining_time:
                fitted.append(task)
                remaining_time -= task.duration
            else:
                self.skipped_tasks.append(task)
        self.tasks = fitted

    def generate_plan(self) -> None:
        """Sort and filter tasks, then build the scheduled_items timeline from start_time."""
        self.sort_tasks()
        self.filter_tasks()

        current_time = datetime.strptime(self.start_time, "%H:%M")
        self.scheduled_items = []
        for task in self.tasks:
            self.scheduled_items.append((current_time.strftime("%H:%M"), task))
            current_time += timedelta(minutes=task.duration)

    def explain(self) -> str:
        """Return a human-readable summary of what was scheduled and skipped."""
        if self.scheduled_items:
            included = ", ".join(f"{task.name} ({task.priority})" for _, task in self.scheduled_items)
            parts = [f"Included {len(self.scheduled_items)} task(s): {included}."]
        else:
            parts = ["No tasks were scheduled."]

        if self.skipped_tasks:
            skipped = ", ".join(f"'{task.name}'" for task in self.skipped_tasks)
            parts.append(f"Skipped {len(self.skipped_tasks)} task(s) due to insufficient time: {skipped}.")

        return " ".join(parts)

    def display_plan(self) -> str:
        """Return the scheduled tasks formatted as a time-ordered plan string."""
        if not self.scheduled_items:
            return "No tasks scheduled."
        return "\n".join(f"{time} — {task}" for time, task in self.scheduled_items)
