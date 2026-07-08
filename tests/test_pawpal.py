import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task, expand_recurring_tasks


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


def test_sort_by_time_orders_timed_tasks_chronologically():
    scheduler = Scheduler(
        tasks=[
            Task(name="Feed dinner", duration=15, priority="medium", pet_name="Rex", preferred_time="18:00"),
            Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00"),
            Task(name="Brush fur", duration=10, priority="low", pet_name="Rex"),
        ],
        available_time=90,
        start_time="08:00",
    )

    scheduler.sort_by_time()

    assert [t.name for t in scheduler.tasks] == ["Morning walk", "Feed dinner", "Brush fur"]


def test_get_tasks_by_pet_returns_only_that_pets_tasks():
    owner = Owner(name="Jamie")
    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task(name="Morning walk", duration=30, priority="high", pet_name=dog.name))
    cat.add_task(Task(name="Feed breakfast", duration=15, priority="medium", pet_name=cat.name))

    assert [t.name for t in owner.get_tasks_by_pet("Rex")] == ["Morning walk"]


def test_get_tasks_by_status_filters_completed_tasks():
    owner = Owner(name="Jamie")
    pet = Pet(name="Rex", species="Dog")
    owner.add_pet(pet)
    done_task = Task(name="Brush fur", duration=10, priority="low", pet_name=pet.name)
    done_task.mark_complete()
    pet.add_task(done_task)
    pet.add_task(Task(name="Morning walk", duration=30, priority="high", pet_name=pet.name))

    incomplete = owner.get_tasks_by_status(is_complete=False)

    assert [t.name for t in incomplete] == ["Morning walk"]


def test_expand_recurring_tasks_creates_one_occurrence_per_day():
    daily_task = Task(
        name="Give medication", duration=5, priority="high", pet_name="Rex", recurrence="daily"
    )

    occurrences = expand_recurring_tasks([daily_task], start_date=date(2026, 7, 7), num_days=3)

    assert [o.occurrence_date for o in occurrences] == ["2026-07-07", "2026-07-08", "2026-07-09"]
    assert len({o.task_id for o in occurrences}) == 3


def test_next_occurrence_advances_daily_task_by_one_day():
    task = Task(name="Give medication", duration=5, priority="high", pet_name="Rex", recurrence="daily")

    next_task = task.next_occurrence(today=date(2026, 7, 7))

    assert next_task.occurrence_date == "2026-07-08"
    assert next_task.is_complete is False
    assert next_task.task_id != task.task_id


def test_next_occurrence_advances_weekly_task_by_seven_days():
    task = Task(name="Nail trim", duration=10, priority="low", pet_name="Rex", recurrence="weekly")

    next_task = task.next_occurrence(today=date(2026, 7, 7))

    assert next_task.occurrence_date == "2026-07-14"


def test_next_occurrence_returns_none_for_non_recurring_task():
    task = Task(name="One-off vet visit", duration=45, priority="high", pet_name="Rex")

    assert task.next_occurrence(today=date(2026, 7, 7)) is None


def test_mark_complete_returns_next_occurrence_for_recurring_task():
    task = Task(name="Give medication", duration=5, priority="high", pet_name="Rex", recurrence="daily")

    next_task = task.mark_complete(today=date(2026, 7, 7))

    assert task.is_complete is True
    assert next_task is not None
    assert next_task.occurrence_date == "2026-07-08"


def test_mark_complete_returns_none_for_non_recurring_task():
    task = Task(name="One-off vet visit", duration=45, priority="high", pet_name="Rex")

    assert task.mark_complete() is None
    assert task.is_complete is True


def test_complete_task_auto_spawns_next_occurrence_for_recurring_task():
    pet = Pet(name="Rex", species="Dog")
    medication = Task(name="Give medication", duration=5, priority="high", pet_name=pet.name, recurrence="daily")
    pet.add_task(medication)

    spawned = pet.complete_task(medication.task_id, today=date(2026, 7, 7))

    assert medication.is_complete is True
    assert spawned is not None
    assert spawned.occurrence_date == "2026-07-08"
    assert len(pet.tasks) == 2
    assert spawned in pet.tasks


def test_complete_task_does_not_spawn_for_non_recurring_task():
    pet = Pet(name="Rex", species="Dog")
    task = Task(name="One-off vet visit", duration=45, priority="high", pet_name=pet.name)
    pet.add_task(task)

    spawned = pet.complete_task(task.task_id, today=date(2026, 7, 7))

    assert spawned is None
    assert len(pet.tasks) == 1


def test_detect_conflicts_flags_overlapping_preferred_times():
    scheduler = Scheduler(
        tasks=[
            Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00"),
            Task(name="Feed breakfast", duration=15, priority="medium", pet_name="Whiskers", preferred_time="08:15"),
            Task(name="Brush fur", duration=10, priority="low", pet_name="Rex", preferred_time="09:00"),
        ],
        available_time=90,
        start_time="08:00",
    )

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    names = {conflicts[0][0].name, conflicts[0][1].name}
    assert names == {"Morning walk", "Feed breakfast"}


def test_detect_conflicts_flags_two_tasks_at_the_exact_same_time():
    scheduler = Scheduler(
        tasks=[
            Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00"),
            Task(name="Litter box cleanup", duration=10, priority="medium", pet_name="Whiskers", preferred_time="08:00"),
        ],
        available_time=90,
        start_time="08:00",
    )

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1


def test_detect_conflicts_returns_empty_list_when_no_overlap():
    scheduler = Scheduler(
        tasks=[
            Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00"),
            Task(name="Feed breakfast", duration=15, priority="medium", pet_name="Whiskers", preferred_time="09:00"),
        ],
        available_time=90,
        start_time="08:00",
    )

    assert scheduler.detect_conflicts() == []


def test_get_conflict_warnings_returns_readable_strings_without_raising():
    scheduler = Scheduler(
        tasks=[
            Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00"),
            Task(name="Litter box cleanup", duration=10, priority="medium", pet_name="Whiskers", preferred_time="08:00"),
        ],
        available_time=90,
        start_time="08:00",
    )

    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) == 1
    assert "Morning walk" in warnings[0]
    assert "Litter box cleanup" in warnings[0]
    assert warnings[0].startswith("Warning:")


def test_get_conflict_warnings_returns_empty_list_when_no_conflicts():
    scheduler = Scheduler(
        tasks=[Task(name="Morning walk", duration=30, priority="high", pet_name="Rex", preferred_time="08:00")],
        available_time=90,
        start_time="08:00",
    )

    assert scheduler.get_conflict_warnings() == []
