# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
My output:

Today's Schedule
08:00 — Morning walk (30 min) [priority: high]
08:30 — Feed breakfast (15 min) [priority: medium]
08:45 — Brush fur (10 min) [priority: low]

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | By priority+duration, or chronologically by `Task.preferred_time` (untimed tasks fall back to priority order) |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()`, `Owner.get_tasks_by_pet()`, `Owner.get_tasks_by_status()` | Filter by whether a task fits in available time, by pet, or by completion status |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()` | Flags any two tasks whose `preferred_time`/`end_time` windows overlap; surfaced as warnings in `Scheduler.explain()` |
| Recurring tasks | `expand_recurring_tasks()`, `Task.mark_complete()`, `Task.next_occurrence()`, `Pet.complete_task()` | Pre-expand a recurring `Task` over a date range, or auto-spawn the next occurrence the moment one is completed |

### Sorting behavior

- **`Scheduler.sort_tasks()`** — the original priority-first sort: descending priority (high → low), ties broken by shorter duration. This is what `generate_plan()` uses to decide which tasks earn a spot in the available time.
- **`Scheduler.sort_by_time()`** — sorts tasks chronologically by `Task.preferred_time` (e.g. "08:00" before "09:00"). Tasks with no `preferred_time` have no fixed slot, so they're placed after the timed ones, ordered by the same priority/duration rule as `sort_tasks()`.

### Filtering behavior

- **`Scheduler.filter_tasks()`** — keeps only the tasks that fit in `available_time`, greedily consuming the budget in whatever order `self.tasks` is currently sorted in; anything that doesn't fit is tracked in `skipped_tasks`.
- **`Scheduler.filter_by_pet(pet_name)`** / **`Owner.get_tasks_by_pet(pet_name)`** — restrict to tasks belonging to one pet. The `Scheduler` version narrows `self.tasks` in place (for building a per-pet plan); the `Owner` version is a read-only lookup.
- **`Scheduler.filter_by_status(is_complete)`** / **`Owner.get_tasks_by_status(is_complete)`** — restrict to tasks matching a completion status (e.g. show only what's still outstanding today).

### Conflict detection logic

- **`Scheduler.detect_conflicts()`** — compares every pair of timed tasks (same pet or different) and flags any two whose `[preferred_time, end_time)` windows overlap, including two tasks scheduled at the exact same time. It's a simple O(n²) pairwise comparison — a deliberate readability-over-performance tradeoff explained in [reflection.md](reflection.md) section 2b.
- **`Scheduler.get_conflict_warnings()`** — the "lightweight" wrapper around `detect_conflicts()`: turns each conflicting pair into a human-readable warning string instead of raising, returning an empty list when nothing conflicts. `Scheduler.explain()` appends these warnings to its summary automatically.

### Recurring task logic

- **`expand_recurring_tasks(tasks, start_date, num_days)`** — given a `Task` with `recurrence="daily"` or `"weekly"`, pre-generates one dated copy per applicable day across a date range (e.g. planning a week ahead).
- **`Task.mark_complete(today=None)`** — marking a recurring task complete automatically creates and returns its next occurrence (due `today + timedelta(days=1)` for daily, `+timedelta(days=7)` for weekly); returns `None` for one-off tasks.
- **`Task.next_occurrence(today=None)`** — the pure due-date calculation `mark_complete()` delegates to; also callable on its own.
- **`Pet.complete_task(task_id, today=None)`** — the pet-level entry point: marks the task complete and, if `mark_complete()` returns a next occurrence, adds it straight to the pet's task list.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
