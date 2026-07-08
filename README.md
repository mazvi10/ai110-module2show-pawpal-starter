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
========================================
Today's Schedule
========================================
Daily plan for Sarah:
  08:00 — Biscuit: Morning walk (30 min) [priority: high]
  08:30 — Biscuit: Feeding (10 min) [priority: high]
  08:40 — Milo: Give meds (5 min) [priority: high]
  08:45 — Milo: Play time (20 min) [priority: medium]

Why this plan:
Planned 4 task(s) using 65 of 90 available minutes.
  Included Biscuit's Morning walk (30 min, high priority).
  Included Biscuit's Feeding (10 min, high priority).
  Included Milo's Give meds (5 min, high priority).
  Included Milo's Play time (20 min, medium priority).
  Skipped Biscuit's Grooming — not enough time left (needs 40 min).
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.6, pytest-9.1.1, pluggy-1.6.0 -- /Users/mazvitanhidza/ai110/ai110-module2show-pawpal-starter/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/mazvitanhidza/ai110/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 15 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  6%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 13%]
tests/test_pawpal.py::test_filter_tasks_excludes_completed_by_default PASSED [ 20%]
tests/test_pawpal.py::test_filter_tasks_by_category PASSED               [ 26%]
tests/test_pawpal.py::test_sort_breaks_priority_ties_by_shortest_duration PASSED [ 33%]
tests/test_pawpal.py::test_completing_daily_task_spawns_next_day_instance PASSED [ 40%]
tests/test_pawpal.py::test_completing_weekly_task_spawns_seven_days_later PASSED [ 46%]
tests/test_pawpal.py::test_completing_one_shot_task_spawns_nothing PASSED [ 53%]
tests/test_pawpal.py::test_spawned_instance_not_due_until_its_date PASSED [ 60%]
tests/test_pawpal.py::test_generate_plan_includes_due_recurring_task PASSED [ 66%]
tests/test_pawpal.py::test_generate_plan_orders_entries_chronologically PASSED [ 73%]
tests/test_pawpal.py::test_detect_conflicts_flags_identical_times PASSED [ 80%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_fixed_times PASSED [ 86%]
tests/test_pawpal.py::test_detect_conflicts_empty_when_times_dont_overlap PASSED [ 93%]
tests/test_pawpal.py::test_invalid_fixed_time_falls_back_to_flexible_without_crashing PASSED [100%]

============================== 15 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling


| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority(tasks)`|  sorts on a two-part key `(priority, duration)`: high→medium→low, then shortest-first to break ties. `generate_plan()` also sorts the final plan by `start_minutes` for chronological order.
 |
| Filtering |`Scheduler.filter_tasks(pet, status, category, due_on)` | one helper with optional filters (by pet, status, category, or due date). `get_single_pet_tasks(pet)` wraps it for a single pet |
| Conflict handling | `Scheduler.detect_conflicts()`|eturns warning strings (never crashes). Two tasks conflict when their time windows overlap (`second.start < first.start + first.duration`), since the owner can't be in two places at once. |
| Recurring tasks | `Pet.complete_task(task, today)`| arks it done and auto-spawns the next occurrence with `Task.next_occurrence()`, dated `today + RECURRENCE_DELTAS[recurrence]` (daily +1 day, weekly +7). `Task.is_due(today)` keeps future occurrences out of today's plan.
 |

## ✨ Features

- **Priority sorting** — `sort_by_priority()` orders tasks on a two-part key
  `(priority, duration)`: high → medium → low, then shortest-first to break
  ties (so more short tasks fit). Unknown priorities sort last. The sort is
  stable, so fully-tied tasks keep their insertion order.

- **Sorting by time (chronological plan)** — after fitting tasks,
  `generate_plan()` sorts the final schedule by `start_minutes` so the day
  reads top-to-bottom in clock order, regardless of the order tasks were picked.

- **Greedy time-budget planning** — `generate_plan()` pools every pet's tasks
  due today, walks them in priority order, and includes each one that still
  fits in the remaining minutes; the rest go to a `skipped` list. Tasks are
  laid out starting at 08:00.

- **Fixed-time appointments** — a task with a `preferred_time` ("HH:MM") is
  pinned to that time instead of flowing with the greedy cursor. Blank or
  malformed times are treated as flexible rather than crashing the plan
  (`_clock_to_minutes` parses leniently).

- **Conflict warnings** — `detect_conflicts()` scans the placed plan and flags
  any two tasks whose time windows overlap (the owner can't be in two places at
  once). It only reads already-placed times, so it never crashes; back-to-back
  tasks that merely touch (e.g. 08:00–08:30 then 08:30) are not flagged.

- **Daily & weekly recurrence** — completing a task via `Pet.complete_task()`
  marks it done and auto-spawns its next occurrence with
  `Task.next_occurrence()`, dated `today + 1 day` (daily) or `+ 7 days`
  (weekly). `timedelta` keeps month/year rollovers correct (Jul 31 → Aug 1).
  The finished task stays as history; one-shot tasks spawn nothing.

- **Due-date awareness** — `Task.is_due(today)` keeps future recurring
  occurrences out of today's plan until their date arrives, and drops tasks
  already completed for the day.

- **Flexible filtering** — `filter_tasks(pet, status, category, due_on)` is the
  single source of truth for task selection; each argument narrows the view
  (by pet, status, category, or due date). `get_single_pet_tasks()` wraps it
  for a per-pet, priority-sorted view.

- **Plan explanation** — `explain_plan()` reports how many minutes were used,
  which tasks were included, and why others were skipped, so the schedule is
  transparent rather than a black box.

## 📸 Demo Walkthrough

Run `streamlit run app.py`, then follow along:

1. **Add an owner** (e.g. `Sarah`) — switch between owners from the dropdown.
2. **Add a pet** (e.g. `Biscuit`, dog, 3); it shows up in the pets table.
3. **Add tasks** with priority, duration, repeat, and an optional fixed time.
   Each pet's task table is already **sorted by priority, then shortest first**.
4. **Set time available and generate** — tasks are fitted into your budget and
   shown as a table in **chronological order**.
5. **Review the results** — "Why this plan" lists included/**skipped** tasks,
   overlapping fixed times raise a **conflict warning**, and completed
   daily/weekly tasks **recur** on their next due date.

**Main.py results**
```
================================================
Sorting: pending tasks, high-priority & shortest-first
================================================
  Give meds (5 min, high priority, meds)
  Feeding (10 min, high priority, feeding)
  Morning walk (30 min, high priority, walk)
  Play time (20 min, medium priority, enrichment)
  Grooming (40 min, low priority, grooming)
  ^ Feeding (10 min) sorts before Morning walk (30 min): same
    priority, shorter duration wins the tie.

================================================
Filtering: by pet, by status, by category
================================================
Milo's pending tasks:
  Play time (20 min, medium priority, enrichment)
  Give meds (5 min, high priority, meds)

Completed tasks (excluded from plans):
  Early potty break (5 min, high priority, walk)

Only 'walk' tasks that are still pending:
  Morning walk (30 min, high priority, walk)

================================================
Today's Schedule
================================================
Daily plan for Sarah:
  08:00 — Milo: Give meds (5 min) [priority: high]
  08:05 — Biscuit: Feeding (10 min) [priority: high]
  08:15 — Biscuit: Morning walk (30 min) [priority: high]
  08:45 — Milo: Play time (20 min) [priority: medium]

Why this plan:
Planned 4 task(s) using 65 of 90 available minutes.
  Included Milo's Give meds (5 min, high priority).
  Included Biscuit's Feeding (10 min, high priority).
  Included Biscuit's Morning walk (30 min, high priority).
  Included Milo's Play time (20 min, medium priority).
  Skipped Biscuit's Grooming — not enough time left (needs 40 min).

================================================
Conflict detection: two tasks at 08:00
================================================
Daily plan for Sarah:
  08:00 — Milo: Give meds (10 min) [priority: high]
  08:00 — Biscuit: Morning walk (30 min) [priority: high]

⚠ Scheduler found 1 conflict(s):
  - Milo's Give meds (08:00) overlaps Biscuit's Morning walk (08:00).

================================================
Recurrence: completing tasks on 2026-07-07
================================================
Completed 'Give meds' (daily) -> status now 'completed'.
  Next 'Give meds' auto-scheduled for 2026-07-08 (was 2026-07-07).
Completed 'Bath' (weekly) -> status now 'completed'.
  Next 'Bath' auto-scheduled for 2026-07-14 (was 2026-07-07).

Milo's task list now (completed originals + next occurrences):
  Give meds: status=completed, due=—
  Bath: status=completed, due=—
  Give meds: status=pending, due=2026-07-08
  Bath: status=pending, due=2026-07-14
```


