import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(name="Feed breakfast", duration=15, priority="medium", pet_name="Rex")
    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Rex", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Morning walk", duration=30, priority="high", pet_name=pet.name))

    assert len(pet.tasks) == 1
