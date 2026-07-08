"""Testing ground for PawPal+ logic layer (pawpal_system.py)."""

from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Jamie", available_time=90)

dog = Pet(name="Rex", species="Dog")
cat = Pet(name="Whiskers", species="Cat")
owner.add_pet(dog)
owner.add_pet(cat)

dog.add_task(Task(name="Morning walk", duration=30, priority="high", pet_name=dog.name))
dog.add_task(Task(name="Brush fur", duration=10, priority="low", pet_name=dog.name))
cat.add_task(Task(name="Feed breakfast", duration=15, priority="medium", pet_name=cat.name))

scheduler = Scheduler.from_owner(owner, start_time="08:00")
scheduler.generate_plan()

print("Today's Schedule")
print(scheduler.display_plan())
print()
print(scheduler.explain())
