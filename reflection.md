# PawPal+ Project Reflection

## 1. System Design

1. Set up a pet (and owner) profile
As a pet owner, I want to enter my basic info and create a profile for my pet, so that the app knows who it's planning care for.

When the user first opens the app, they provide a few basic details about themselves and their pet — the pet's name and type/breed (e.g. "Biscuit, a Golden Retriever"). This profile is the foundation everything else attaches to, and the user can come back and update it later.

System captures: owner name, pet name, pet type/breed
User expects: the profile to persist and appear throughout the app

2. Add or edit a care task
As a pet owner, I want to add the things my pet needs (walks, feeding, meds, grooming, enrichment) and say how long each takes and how important it is, so that the app has a full list of what needs to happen.

The user adds tasks one at a time, giving each a name plus — at minimum — a duration (minutes) and a priority (high / medium / low). They can edit or remove tasks later. This collection is what the scheduler reasons over.

System captures: task name, duration, priority (optionally preferred time or recurrence)
User expects: to see their running task list and be able to change it

3. Generate and view today's plan
As a pet owner, I want to tell the app how much time I have and have it build a daily schedule from my tasks, so that I know exactly what to do and when — without dropping anything important.

The user requests a plan, providing constraints like total time available. The scheduler sorts tasks by priority and duration, fits what it can into the available time, and skips or defers lower-priority tasks when time runs out. The result is a clear, time-ordered schedule — ideally with a short explanation of why it looks that way.

System uses: the task list plus constraints (time, priority, preferences)
User expects: a clean timeline (e.g. 08:00 — Morning walk (30 min) [priority: high]) and the reasoning behind it

Overall flow
Set up your pet → add what needs doing → get your plan for the day.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Overview
The design has four classes split cleanly into two roles: Owner and Pet hold data, while Scheduler handles all decision-making logic, with Task as the shared unit of information that flows between them.

Classes and responsibilities
Owner
Represents the person using the app. Holds a name, a list of pets (supporting one or many), and available_time — the day's time budget. Its responsibility is managing the owner's collection of pets and flattening all their tasks into a single list (get_all_tasks()) so the scheduler can weigh them against each other regardless of which pet they belong to.

Pet
Represents a single animal. Holds name, species, and its own list of tasks. Its responsibility is direct task management for that pet — adding, editing, removing, and listing tasks (add_task, edit_task, remove_task, list_tasks).

Task
Represents one unit of care (a walk, a feeding, etc.). Holds the minimum fields needed to schedule it: name, duration, priority, and pet_name — the last of which traces a task back to its owning pet once tasks from multiple pets are combined into one list. Its responsibility is representing that data and computing a priority_score() for sorting.

Scheduler
The engine of the system. Holds the working state for building a plan: the tasks to schedule, available_time, start_time, plus the results (scheduled_items, skipped_tasks). Its responsibility is the actual decision-making — sorting tasks by priority (sort_tasks), dropping ones that don't fit in the available time (filter_tasks), assembling the final timeline (generate_plan), justifying the choices (explain), and formatting the output (display_plan).

Relationships
*Owner -- Pet (composition, 1-to-many) — an owner has one or more pets; pets belong to exactly one owner.
*Pet -- Task (composition, 1-to-many) — a pet has many tasks; each task belongs to one pet.
Owner ..> Scheduler (dependency) — the owner supplies the scheduler with its flattened tasks and time constraint, but doesn't own or contain the scheduler.
Scheduler ..> Task (dependency) — the scheduler reads, sorts, and filters tasks, but doesn't own them; ownership stays with Pet.
This is the simplified/MVP version of the design — it reflects only the attributes and methods required by the README's core loop (owner/pet info → tasks with duration+priority → generate and display a plan), with earlier stretch features (categories, recurrence, conflict handling, completion tracking) deliberately left out for now.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes — after reviewing the initial class stubs, I found a few places where the design didn't fully support its own methods, and updated both pawpal_system.py and diagrams/uml_draft.mmd to fix them.

The main change was adding a task_id field to Task. Originally, Pet.edit_task() and Pet.remove_task() both took a task_id parameter, but Task had no task_id attribute anywhere — there was nothing for those methods to actually match against. I added an auto-generated task_id (via uuid) so tasks can be reliably identified and updated, even if two tasks share the same name.

I also tightened a few relationships that existed in name only:

Pet.add_task() now force-sets task.pet_name to the pet it's being added to, instead of trusting whoever created the Task to set it correctly — this prevents a task from silently pointing to the wrong pet.
Task.priority is now validated against "low"/"medium"/"high" on creation, since nothing previously stopped a typo like "High" from silently breaking the scheduler's sorting later.
Owner.add_pet() now rejects duplicate pet names, since pet-name lookups (get_pet()) and grouping the plan by pet assume names are unique.
I made these changes because they were bugs waiting to happen once real scheduling logic was implemented — better to catch a missing task_id or an unvalidated priority at design time than debug a silently wrong daily plan later. I updated the UML diagram to match by adding task_id to Task.

Added an is_complete flag and mark_complete() method to Task so completion status can be tracked and tested, updated uml_draft.mmd to match.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts()` checks every pair of timed tasks for overlap, which is O(n²): for a task list of size n, it does roughly n²/2 comparisons. I asked my AI assistant how this could be simplified for readability or performance, and it offered two directions:

1. A purely readability-focused rewrite using `itertools.combinations()` instead of a manual nested loop with `enumerate`/index-slicing — same O(n²) cost, but reads more like "for every pair of tasks" instead of exposing the loop bookkeeping.
2. A performance-focused rewrite that sorts tasks by start time first, then breaks out of the inner loop early once a task starts after the current one has already ended (nothing later in a sorted list can still overlap it). Still O(n²) worst case, but much faster in the common case where most tasks don't overlap.

I kept option 1 and rejected option 2. The `itertools.combinations` version is strictly easier to read with no downside, so it was an easy adopt. The sweep-line version is "more Pythonic" and asymptotically kinder in the average case, but it asks the reader to trust a `break` statement's correctness ("why is it safe to stop here?") instead of seeing the comparison happen directly — for a feature whose entire audience is one pet owner's daily task list (realistically a dozen or so tasks, never thousands), that's added cognitive load for a performance gain that will never matter at this scale. I'd reconsider if PawPal+ ever scheduled a shared household's or a boarding facility's tasks across many pets and owners at once, where n could grow large enough for the difference to be real.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
