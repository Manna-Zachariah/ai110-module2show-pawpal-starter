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

The scheduler considers three kinds of constraint, and I treated them as layered rather than equal. The first layer is required: every task has a `priority` (high/medium/low, via `priority_score()`) and a `duration`, and `available_time` is the hard budget `filter_tasks()` enforces — a task either fits or gets pushed into `skipped_tasks`, no partial scheduling. I made this layer required because it's the minimum the README's core loop asks for (owner/pet info → tasks with duration+priority → a plan), and a pet owner can't act on a plan that silently drops something without saying so.

The second layer is optional and additive: `preferred_time` (and the `recurrence` it enables). A task doesn't need a preferred time to be schedulable — `sort_by_time()` just pushes untimed tasks to the end, ordered by the same priority/duration rule as everything else — but when it's present, it unlocks `detect_conflicts()`/`get_conflict_warnings()` and chronological ordering. I decided priority+duration+available_time mattered most because they're load-bearing for every plan the app produces, while `preferred_time` is enrichment: valuable when an owner supplies it, but the system has to degrade gracefully without it.

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

I used my AI coding assistant across the full lifecycle: drafting the initial UML stubs from my scenario description, implementing the scheduling logic increment by increment (sorting, filtering, conflict detection, recurrence), writing the pytest suite, wiring the backend into the Streamlit UI, and finally auditing my own UML diagram against the finished code. The most effective feature by far was having the assistant directly read and diff my source files against my design docs — instead of me manually re-reading `pawpal_system.py` method-by-method against `uml_draft.mmd`, I could ask "does this UML still match this code?" and get back a precise, attribute-by-attribute and method-by-method list of what had drifted (missing `preferred_time`/`recurrence`/`occurrence_date` fields, `mark_complete()` returning `Task` instead of `void`, the whole conflict-detection surface never added to the diagram). The second most useful pattern was asking it to actually run things and show me real output — executing `main.py` and the pytest suite, and briefly launching the Streamlit app to confirm it rendered without a traceback — rather than trusting a description of what the code "should" do.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Two examples stand out. The design-level one is documented in section 2b: my assistant offered a sweep-line optimization for `detect_conflicts()` that would have been asymptotically kinder but required trusting a `break` statement's correctness instead of seeing every comparison happen directly; I rejected it because a single owner's daily task list will never be large enough for the performance gain to matter, and the `itertools.combinations()` version is strictly easier to read. The process-level one happened during the packaging phase: when I asked whether my UML diagram still matched my code, the assistant started applying an edit directly to `uml_draft.mmd` before I'd actually decided I wanted the historical draft touched. I stopped it mid-edit and asked it to just answer the question first — which is how I ended up deciding to keep `uml_draft.mmd` as the untouched Phase-1 record and have the assistant write the corrected diagram to a new `uml_final.mmd` instead. I verified the eventual diagram by actually rendering it through the Mermaid CLI to catch syntax errors, not by just reading the source and trusting it was valid.

**c. Working in separate sessions**

- How did using separate chat sessions for different phases help you stay organized?

I kept design and implementation (the UML draft, `pawpal_system.py`, the test suite, and reflection sections 1–2) in earlier sessions, and used a dedicated later session purely for the packaging phase — reflecting the algorithmic layer in the UI, reconciling the UML, and polishing the README. Splitting it this way meant each session only carried the context relevant to its one deliverable: the packaging session never had to re-litigate why `Task` needs a `task_id` or why `detect_conflicts()` is O(n²), it could just load the finished `pawpal_system.py` as ground truth and work forward from there. It also made stale documentation obvious — arriving fresh at `uml_draft.mmd` in a new session immediately surfaced how much had been added since Phase 1, in a way a single continuous session might have let slide as "already discussed."

**d. Being the lead architect**

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

The AI is fast and thorough at mechanical work — diffing a diagram against code, wiring a UI to methods that already exist, drafting a features list or demo walkthrough from real behavior — but it acts as soon as it's confident, not once I've confirmed the plan is actually what I wanted. Being the lead architect meant deciding the boundaries myself: which files were fine to change without asking (`app.py`, `README.md`) versus which needed my sign-off first (`uml_draft.mmd`, or anything treated as a source-of-truth artifact), and which tradeoffs (readability vs. performance, backend-general vs. UI-local logic) were mine to make because they depend on judgment about the system's actual scale and audience, not just correctness. The assistant can tell me what's inconsistent or what's technically possible; only I know what this specific app is supposed to be for a pet owner with a dozen daily tasks, and that context is what should drive every tradeoff it surfaces.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I focused testing on the behaviors most likely to hide an off-by-one or silent-wrong-answer bug rather than the simple getters/setters: `sort_tasks()`/`sort_by_time()` ordering (including where untimed tasks land), `filter_tasks()` respecting `available_time` at the exact-fit boundary, `detect_conflicts()` correctly flagging exact-same-time and truly-overlapping tasks while *not* flagging two tasks that just touch back-to-back, the recurrence chain (`mark_complete()` → `next_occurrence()` → `Pet.complete_task()`) producing the right next date for `daily` vs `weekly`, and input validation rejecting an invalid `priority`/`recurrence` instead of silently accepting a typo.

These mattered because a pet owner trusts the plan without re-deriving it by hand — a boundary bug in `filter_tasks()` could silently drop a task that should have fit, an off-by-one in `detect_conflicts()` could either miss a real double-booking or cry wolf on two tasks that don't actually overlap, and a bad recurrence date could mean a medication reminder never comes back. Those are exactly the failure modes that don't show up just from reading the code or running it once by hand with `main.py` — they need boundary-focused test cases to catch.

**b. Confidence**

**Confidence Level: ⭐⭐⭐⭐☆ (4/5)**

All 26 tests in `tests/test_pawpal.py` pass, covering the core scheduling paths: priority/duration sorting, chronological sorting, recurring-task generation (daily/weekly), conflict detection (including exact-overlap and back-to-back boundaries), time-budget filtering (including the exact-fit boundary), and input validation (invalid `priority`/`recurrence` raise `ValueError`). That gives me solid confidence in the scheduler's core logic — the pieces most likely to have subtle bugs (off-by-one boundaries in time comparisons, recurrence date math) are explicitly exercised and pass.

I'm holding back from 5/5 because coverage isn't complete: `Owner.add_pet()`'s duplicate-name rejection, `Task.end_time` when `preferred_time` is `None`, and `Task.__str__`/`priority_score()` aren't directly tested. There's also no test for multi-day recurring expansion combined with conflict detection together (each is tested in isolation), and no randomized/property-based testing to shake out inputs I haven't thought of.

If I had more time, I'd test next:
- `Owner.add_pet()` rejecting a duplicate pet name.
- `Task.end_time` returning `None` when `preferred_time` is unset.
- A combined scenario: recurring tasks expanded across several days, then run through `detect_conflicts()` and `generate_plan()` together, to catch integration bugs the isolated unit tests wouldn't.
- Malformed `preferred_time`/`start_time` strings (e.g. `"9:00"` vs `"09:00"`, or invalid times) to see how gracefully the scheduler degrades.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the conflict-warning feature end to end, not just as a backend method. `Scheduler.get_conflict_warnings()` is a single source of truth that now drives two different moments in the UI — a live check the instant two tasks overlap (even across different pets, before any plan is generated), and the same warnings surfaced again when a plan is actually built — so a pet owner sees the same fact from two angles instead of the app quietly making a scheduling decision for them. It's a small feature, but it's the one place where the "smart" backend logic and the UI genuinely reinforce each other rather than the UI just being a thin form on top of a class.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

`Pet.edit_task()` exists in the backend and is fully tested, but `app.py` never calls it — the UI only lets you add, complete, or remove a task, not correct one after the fact (e.g. fix a typo'd duration or move a preferred time). That's the clearest remaining gap between what the system *can* do and what the UI *lets you* do. I'd also want real persistence — everything currently lives in `st.session_state`, so the whole plan disappears on a page refresh — and I'd extend the UI to actually use `expand_recurring_tasks()` for a multi-day view, since right now recurrence only shows up one occurrence at a time even though the backend can already project a task a week out.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The gap between "the backend supports it" and "the user can actually see and use it" doesn't close on its own — it takes a deliberate pass to go back through every method on `Scheduler`/`Pet`/`Task` and ask whether the UI actually exposes it, the same way the UML-vs-code audit caught documentation that had quietly gone stale. Both gaps (UI-vs-backend, diagram-vs-code) happened for the same reason: I kept adding capability to the lowest layer (the class methods) because that's where an AI assistant and I could iterate fastest, and the layers meant to reflect that capability back to a human — the UI, the diagram, the README — only caught up when I explicitly stopped to reconcile them. The lesson isn't "build UI and docs continuously instead," it's that reconciliation has to be its own deliberate step, not an assumed side effect of writing the logic.
