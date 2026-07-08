# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## ✨ Features

- **Owner & pet profiles** — one owner, any number of pets, each with its own independent task list.
- **Task tracking** — add care tasks with a name, duration, priority (`low`/`medium`/`high`), an optional preferred time, and an optional recurrence (`daily`/`weekly`).
- **Priority-based scheduling** — `Scheduler.sort_tasks()` orders the day's plan by descending priority, then shortest duration, so a long low-priority task can never bump something urgent.
- **Chronological scheduling** — `Scheduler.sort_by_time()` orders the same tasks by time of day instead, for owners who think in "what's next" rather than "what matters most."
- **Time-budget filtering** — `Scheduler.filter_tasks()` fits as many tasks as possible into the owner's available time and tracks whatever gets skipped, so nothing silently disappears from the plan.
- **Conflict warnings** — `Scheduler.detect_conflicts()` / `get_conflict_warnings()` flag any two tasks — even across different pets — whose preferred times overlap, since one owner can't be in two places at once.
- **Recurring tasks** — completing a `daily`/`weekly` task automatically spawns its next dated occurrence (`Task.mark_complete()`, `Task.next_occurrence()`, `Pet.complete_task()`); `expand_recurring_tasks()` can also pre-expand a recurrence across a date range.
- **Filtering & lookup** — narrow the task list by pet or completion status (`Scheduler.filter_by_pet()`/`filter_by_status()`, `Owner.get_tasks_by_pet()`/`get_tasks_by_status()`).
- **Plan explanations** — `Scheduler.explain()` summarizes what was scheduled, what was skipped and why, and any conflicts found, in plain language.

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

Run the full test suite with:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 26 tests) covers:

- **Sorting** — `sort_tasks()` orders by descending priority then shorter duration; `sort_by_time()` orders timed tasks chronologically and pushes untimed tasks to the end.
- **Recurring tasks** — completing a `daily`/`weekly` task auto-spawns the correctly-dated next occurrence (`Task.mark_complete()`, `Task.next_occurrence()`, `Pet.complete_task()`), non-recurring tasks return `None`, and `expand_recurring_tasks()` generates one occurrence per applicable day.
- **Conflict detection** — `detect_conflicts()`/`get_conflict_warnings()` flag overlapping and exact-same-time tasks, but correctly ignore back-to-back tasks that just touch at the boundary.
- **Task filtering/lookup** — `filter_tasks()` respects the `available_time` budget (including the exact-fit boundary) and tracks skipped tasks; `Owner.get_tasks_by_pet()`/`get_tasks_by_status()` and `Scheduler.filter_by_pet()`/`filter_by_status()` narrow correctly.
- **Edge cases & validation** — an empty task list produces a clean "no tasks" plan; invalid `priority`/`recurrence` values raise `ValueError`; `edit_task()`/`remove_task()` handle an unknown `task_id`.

Sample test output:

```
======================================================================================================================================== test session starts =========================================================================================================================================
platform darwin -- Python 3.13.0, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/mannameriahzachariah/AI110/Week4/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 26 items                                                                                                                                                                                                                                                                                   

tests/test_pawpal.py ..........................                                                                                                                                                                                                                                                [100%]

========================================================================================================================================= 26 passed in 0.04s =========================================================================================================================================
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

### What you can do in the UI

- **Owner & Pets** — enter an owner name and add one or more pets (name + species).
- **Tasks** — for the selected pet, add a task with a title, duration, priority, an optional preferred time (enables conflict checking), and a recurrence. Every task shows up in a table with its time, recurrence, and status.
- **Manage tasks** — from the "Manage tasks" expander, mark any task complete (auto-creating its next occurrence if it recurs) or remove it outright.
- **Live conflict check** — the moment two tasks across *any* of your pets overlap in time, a warning appears immediately below the task list — before you've even generated a schedule.
- **Build Today's Plan** — set your available time and start time, choose to order tasks by priority or by time of day, and generate the plan.

### Example workflow

1. Enter an owner name and add a pet, e.g. "Rex" (dog).
2. Add a few tasks for Rex: "Morning walk" (30 min, high priority, 08:00), "Give medication" (5 min, high priority, 08:00, daily), "Brush fur" (10 min, low priority, no set time).
3. Because "Morning walk" and "Give medication" both land at 08:00, a conflict warning appears immediately under the task list — no need to generate a schedule first to find out.
4. Set available time (e.g. 60 minutes) and a start time (e.g. 08:00), choose "Priority" ordering, and click **Generate schedule**.
5. The app displays the plan as a table (time, task, pet, priority, duration), lists any tasks skipped for not fitting in the available time, and repeats the conflict warning so it isn't missed.
6. Expand **"Why this plan?"** to read `Scheduler.explain()`'s plain-language summary of what was included, what was skipped, and why.
7. Mark "Give medication" complete — since it's `daily`, its next occurrence is automatically added to Rex's task list for tomorrow.

### Key Scheduler behaviors on display

- **Sorting** — switching between "Priority" and "Time of day" swaps `sort_tasks()` for `sort_by_time()`, visibly reordering the generated plan.
- **Conflict warnings** — `get_conflict_warnings()` surfaces overlapping tasks both live (as tasks are added) and again at schedule-generation time.
- **Time-budget filtering** — `filter_tasks()` decides what fits; anything left over shows up as a skipped-task warning instead of silently vanishing from the plan.
- **Recurrence** — completing a `daily`/`weekly` task calls `Pet.complete_task()`, which auto-spawns and displays the next occurrence.

### Sample Output from running main.py

```
--- Tasks in the order they were added (out of order by time) ---
09:00 — Give medication (5 min) [priority: high]
08:00 — Morning walk (30 min) [priority: high]
(unscheduled) — Brush fur (10 min) [priority: low]
08:15 — Feed breakfast (15 min) [priority: medium]
08:00 — Litter box cleanup (10 min) [priority: medium]

Today's Schedule
08:00 — Give medication (5 min) [priority: high]
08:05 — Morning walk (30 min) [priority: high]
08:35 — Litter box cleanup (10 min) [priority: medium]
08:45 — Feed breakfast (15 min) [priority: medium]
09:00 — Brush fur (10 min) [priority: low]

Included 5 task(s): Give medication (high), Morning walk (high), Litter box cleanup (medium), Feed breakfast (medium), Brush fur (low). Warning: 'Morning walk' (Rex, 08:00-08:30) overlaps 'Litter box cleanup' (Whiskers, 08:00-08:10). Warning: 'Morning walk' (Rex, 08:00-08:30) overlaps 'Feed breakfast' (Whiskers, 08:15-08:30).

--- sort_by_time(): same tasks, now chronological ---
08:00 — Morning walk (30 min) [priority: high]
08:00 — Litter box cleanup (10 min) [priority: medium]
08:15 — Feed breakfast (15 min) [priority: medium]
09:00 — Give medication (5 min) [priority: high]
(unscheduled) — Brush fur (10 min) [priority: low]

--- Owner.get_tasks_by_pet('Rex') ---
Give medication (5 min) [priority: high]
Morning walk (30 min) [priority: high]
Brush fur (10 min) [priority: low]

--- Owner.get_tasks_by_status(is_complete=False) ---
Give medication (5 min) [priority: high]
Morning walk (30 min) [priority: high]
Feed breakfast (15 min) [priority: medium]
Litter box cleanup (10 min) [priority: medium]

--- Owner.get_tasks_by_status(is_complete=True) ---
Brush fur (10 min) [priority: low]

--- Scheduler.filter_by_pet('Rex') ---
Give medication (5 min) [priority: high]
Morning walk (30 min) [priority: high]
Brush fur (10 min) [priority: low]

--- Scheduler.filter_by_status(is_complete=False) ---
Give medication (5 min) [priority: high]
Morning walk (30 min) [priority: high]
Feed breakfast (15 min) [priority: medium]
Litter box cleanup (10 min) [priority: medium]

--- Expand recurring tasks over 3 days ---
2026-07-07 — Give medication (5 min) [priority: high]
2026-07-08 — Give medication (5 min) [priority: high]
2026-07-09 — Give medication (5 min) [priority: high]

--- Conflict detection ---
Warning: 'Morning walk' (Rex, 08:00-08:30) overlaps 'Litter box cleanup' (Whiskers, 08:00-08:10).
Warning: 'Morning walk' (Rex, 08:00-08:30) overlaps 'Feed breakfast' (Whiskers, 08:15-08:30).

--- Completing a recurring task auto-spawns its next occurrence ---
Before: Rex has 3 task(s)
Completed 'Give medication' on 2026-07-07.
After:  Rex has 4 task(s)
Auto-spawned: Give medication (5 min) [priority: high] due on 2026-07-08
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
