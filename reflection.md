# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

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

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
