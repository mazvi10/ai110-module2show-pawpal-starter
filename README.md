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


## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
