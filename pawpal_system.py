"""PawPal+ logic layer.

Class stubs generated from diagrams/uml_draft.mmd. No scheduling logic yet —
attributes and method signatures only.
"""

import uuid
from dataclasses import dataclass, field, fields, replace
from datetime import date, datetime, timedelta
from itertools import combinations
from typing import List, Optional, Tuple

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_RECURRENCES = {"none", "daily", "weekly"}


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    pet_name: str
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    is_complete: bool = False
    preferred_time: Optional[str] = None
    recurrence: str = "none"
    occurrence_date: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalize/validate the priority and recurrence strings."""
        self.priority = self.priority.lower()
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")

        self.recurrence = self.recurrence.lower()
        if self.recurrence not in VALID_RECURRENCES:
            raise ValueError(f"recurrence must be one of {VALID_RECURRENCES}, got {self.recurrence!r}")

    def priority_score(self) -> int:
        """Return a numeric weight for the task's priority (high=3, medium=2, low=1)."""
        return {"high": 3, "medium": 2, "low": 1}[self.priority]

    @property
    def end_time(self) -> Optional[str]:
        """Return the HH:MM end time computed from preferred_time + duration, or None."""
        if self.preferred_time is None:
            return None
        start = datetime.strptime(self.preferred_time, "%H:%M")
        return (start + timedelta(minutes=self.duration)).strftime("%H:%M")

    def mark_complete(self, today: Optional[date] = None) -> Optional["Task"]:
        """Mark this task as complete.

        If it recurs ("daily"/"weekly"), automatically create and return the
        next occurrence, due today + timedelta(days=1) or +7 respectively.
        Returns None for non-recurring tasks.
        """
        self.is_complete = True
        return self.next_occurrence(today=today)

    def next_occurrence(self, today: Optional[date] = None) -> Optional["Task"]:
        """Return a fresh, incomplete copy of this task due on its next occurrence.

        The next due date is `today + timedelta(days=1)` for "daily" tasks, or
        `+ timedelta(days=7)` for "weekly" tasks. `today` defaults to the real
        current date; pass it explicitly for deterministic testing. Returns
        None for non-recurring tasks. The new copy gets its own task_id so it
        can be tracked/completed independently of this one.
        """
        if self.recurrence == "none":
            return None

        reference_date = today if today is not None else date.today()
        step_days = {"daily": 1, "weekly": 7}[self.recurrence]
        next_date = reference_date + timedelta(days=step_days)

        return replace(self, task_id=uuid.uuid4().hex, is_complete=False, occurrence_date=next_date.isoformat())

    def __str__(self) -> str:
        """Return a human-readable summary of the task."""
        return f"{self.name} ({self.duration} min) [priority: {self.priority}]"


def expand_recurring_tasks(tasks: List[Task], start_date: date, num_days: int) -> List[Task]:
    """Expand recurring tasks into one concrete occurrence per applicable day.

    Non-recurring tasks are returned unchanged. "daily" tasks get one occurrence
    per day in [start_date, start_date + num_days); "weekly" tasks get one
    occurrence every 7 days starting from start_date. Each occurrence is a copy
    with its own task_id and occurrence_date so it can be tracked/completed
    independently.
    """
    step_by_recurrence = {"daily": 1, "weekly": 7}
    occurrences: List[Task] = []
    for task in tasks:
        if task.recurrence == "none":
            occurrences.append(task)
            continue
        step = step_by_recurrence[task.recurrence]
        for offset in range(0, num_days, step):
            occurrence_date = start_date + timedelta(days=offset)
            occurrences.append(
                replace(task, task_id=uuid.uuid4().hex, occurrence_date=occurrence_date.isoformat())
            )
    return occurrences


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

    def complete_task(self, task_id: str, today: Optional[date] = None) -> Optional[Task]:
        """Mark the task matching task_id complete.

        Task.mark_complete() automatically creates the next occurrence for
        recurring ("daily"/"weekly") tasks; this adds that occurrence to the
        pet's task list. Returns the newly created occurrence, or None if the
        task doesn't recur.
        """
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"no task with task_id {task_id!r} for pet {self.name!r}")

        next_task = task.mark_complete(today=today)
        if next_task is not None:
            self.add_task(next_task)
        return next_task

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

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return the tasks belonging to the pet with the given name."""
        pet = self.get_pet(pet_name)
        return pet.list_tasks() if pet else []

    def get_tasks_by_status(self, is_complete: bool) -> List[Task]:
        """Return every task across all pets matching the given completion status."""
        return [task for task in self.get_all_tasks() if task.is_complete == is_complete]


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

    def sort_by_time(self) -> None:
        """Sort tasks chronologically by preferred_time.

        Tasks without a preferred_time have no fixed slot, so they're placed
        after the timed ones, ordered by the existing priority/duration rule.
        """
        timed = [t for t in self.tasks if t.preferred_time is not None]
        untimed = [t for t in self.tasks if t.preferred_time is None]
        timed.sort(key=lambda t: t.preferred_time)
        untimed.sort(key=lambda t: (-t.priority_score(), t.duration))
        self.tasks = timed + untimed

    def filter_by_pet(self, pet_name: str) -> None:
        """Restrict self.tasks to those belonging to the given pet."""
        self.tasks = [t for t in self.tasks if t.pet_name == pet_name]

    def filter_by_status(self, is_complete: bool) -> None:
        """Restrict self.tasks to those matching the given completion status."""
        self.tasks = [t for t in self.tasks if t.is_complete == is_complete]

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose preferred_time windows overlap.

        Simple O(n^2) pairwise comparison over every timed task -- see
        reflection.md section 2b for why that tradeoff is fine here.
        """
        timed_tasks = [t for t in self.tasks if t.preferred_time is not None]
        return [
            (a, b)
            for a, b in combinations(timed_tasks, 2)
            if a.preferred_time < b.end_time and b.preferred_time < a.end_time
        ]

    def get_conflict_warnings(self) -> List[str]:
        """Return a human-readable warning string for each detected time conflict.

        Lightweight by design: detect_conflicts() does a simple pairwise
        comparison (fine for a single owner's daily task list) and never
        raises -- this just formats whatever it finds into plain strings the
        caller can print/log/display, with an empty list meaning no conflicts.
        """
        warnings = []
        for task_a, task_b in self.detect_conflicts():
            warnings.append(
                f"Warning: '{task_a.name}' ({task_a.pet_name}, {task_a.preferred_time}-{task_a.end_time}) "
                f"overlaps '{task_b.name}' ({task_b.pet_name}, {task_b.preferred_time}-{task_b.end_time})."
            )
        return warnings

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

        warnings = self.get_conflict_warnings()
        if warnings:
            parts.append(" ".join(warnings))

        return " ".join(parts)

    def display_plan(self) -> str:
        """Return the scheduled tasks formatted as a time-ordered plan string."""
        if not self.scheduled_items:
            return "No tasks scheduled."
        return "\n".join(f"{time} — {task}" for time, task in self.scheduled_items)
