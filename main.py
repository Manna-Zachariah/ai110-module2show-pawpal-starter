"""Testing ground for PawPal+ logic layer (pawpal_system.py)."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task, expand_recurring_tasks

owner = Owner(name="Jamie", available_time=90)

dog = Pet(name="Rex", species="Dog")
cat = Pet(name="Whiskers", species="Cat")
owner.add_pet(dog)
owner.add_pet(cat)

# Tasks are added out of chronological order on purpose, to prove sort_by_time() works.
medication = Task(name="Give medication", duration=5, priority="high", pet_name=dog.name,
                   preferred_time="09:00", recurrence="daily")
dog.add_task(medication)
cat.add_task(Task(name="Feed breakfast", duration=15, priority="medium", pet_name=cat.name, preferred_time="08:15"))
dog.add_task(Task(name="Morning walk", duration=30, priority="high", pet_name=dog.name, preferred_time="08:00"))
# Same exact preferred_time as "Morning walk", for a different pet -- Jamie can't do both at once.
cat.add_task(Task(name="Litter box cleanup", duration=10, priority="medium", pet_name=cat.name, preferred_time="08:00"))

brush_fur = Task(name="Brush fur", duration=10, priority="low", pet_name=dog.name)
brush_fur.mark_complete()
dog.add_task(brush_fur)

print("--- Tasks in the order they were added (out of order by time) ---")
for task in owner.get_all_tasks():
    print(f"{task.preferred_time or '(unscheduled)'} — {task}")

scheduler = Scheduler.from_owner(owner, start_time="08:00")
scheduler.generate_plan()

print("\nToday's Schedule")
print(scheduler.display_plan())
print()
print(scheduler.explain())

print("\n--- sort_by_time(): same tasks, now chronological ---")
by_time = Scheduler.from_owner(owner, start_time="08:00")
by_time.sort_by_time()
for task in by_time.tasks:
    print(f"{task.preferred_time or '(unscheduled)'} — {task}")

print("\n--- Owner.get_tasks_by_pet('Rex') ---")
for task in owner.get_tasks_by_pet("Rex"):
    print(task)

print("\n--- Owner.get_tasks_by_status(is_complete=False) ---")
for task in owner.get_tasks_by_status(is_complete=False):
    print(task)

print("\n--- Owner.get_tasks_by_status(is_complete=True) ---")
for task in owner.get_tasks_by_status(is_complete=True):
    print(task)

print("\n--- Scheduler.filter_by_pet('Rex') ---")
rex_scheduler = Scheduler.from_owner(owner, start_time="08:00")
rex_scheduler.filter_by_pet("Rex")
for task in rex_scheduler.tasks:
    print(task)

print("\n--- Scheduler.filter_by_status(is_complete=False) ---")
incomplete_scheduler = Scheduler.from_owner(owner, start_time="08:00")
incomplete_scheduler.filter_by_status(is_complete=False)
for task in incomplete_scheduler.tasks:
    print(task)

print("\n--- Expand recurring tasks over 3 days ---")
occurrences = expand_recurring_tasks(owner.get_all_tasks(), start_date=date(2026, 7, 7), num_days=3)
for task in occurrences:
    if task.occurrence_date:
        print(f"{task.occurrence_date} — {task}")

print("\n--- Conflict detection ---")
warnings = scheduler.get_conflict_warnings()
if warnings:
    for warning in warnings:
        print(warning)
else:
    print("No conflicts detected.")

print("\n--- Completing a recurring task auto-spawns its next occurrence ---")
print(f"Before: Rex has {len(dog.list_tasks())} task(s)")
# `today` is passed explicitly here so the demo output is reproducible; in the
# app you'd call dog.complete_task(medication.task_id) and let it default to
# date.today().
next_occurrence = dog.complete_task(medication.task_id, today=date(2026, 7, 7))
print(f"Completed '{medication.name}' on 2026-07-07.")
print(f"After:  Rex has {len(dog.list_tasks())} task(s)")
print(f"Auto-spawned: {next_occurrence} due on {next_occurrence.occurrence_date}")
