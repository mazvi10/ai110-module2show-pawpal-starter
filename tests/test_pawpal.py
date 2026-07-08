"""Tests for the PawPal+ core system."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should change the task's status to completed."""
    task = Task("Morning walk", "walk", 30, "high")

    assert task.status == "pending"  # sanity check the starting state

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Biscuit", "Golden Retriever", 3)

    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "feeding", 10, "high"))

    assert len(pet.tasks) == 1

    pet.add_task(Task("Grooming", "grooming", 40, "low"))

    assert len(pet.tasks) == 2


def _owner_with_tasks():
    """An owner with one pet carrying a mix of tasks, for scheduler tests."""
    pet = Pet("Biscuit", "dog", 3)
    pet.add_task(Task("Grooming", "grooming", 40, "high"))
    pet.add_task(Task("Feeding", "feeding", 10, "high"))
    done = Task("Old walk", "walk", 30, "low")
    done.mark_complete()
    pet.add_task(done)
    return Owner("Sarah", [pet]), pet


def test_filter_tasks_excludes_completed_by_default():
    """filter_tasks defaults to pending tasks only."""
    owner, _ = _owner_with_tasks()
    scheduler = Scheduler(owner, 90)

    titles = {t.description for t in scheduler.filter_tasks()}

    assert titles == {"Grooming", "Feeding"}  # completed "Old walk" excluded


def test_filter_tasks_by_category():
    """filter_tasks narrows to a single category when asked."""
    owner, _ = _owner_with_tasks()
    scheduler = Scheduler(owner, 90)

    feeding = scheduler.filter_tasks(category="feeding")

    assert [t.description for t in feeding] == ["Feeding"]


def test_sort_breaks_priority_ties_by_shortest_duration():
    """Equal-priority tasks sort shortest-first so more of them fit."""
    owner, _ = _owner_with_tasks()
    scheduler = Scheduler(owner, 90)

    ordered = scheduler.sort_by_priority(scheduler.filter_tasks())

    # Both are high priority, so the 10-min task should come before the 40-min.
    assert [t.description for t in ordered] == ["Feeding", "Grooming"]


def test_completing_daily_task_spawns_next_day_instance():
    """Completing a daily task marks it done and auto-adds a fresh instance
    due tomorrow."""
    today = date(2026, 7, 7)
    pet = Pet("Milo", "cat", 5)
    meds = Task("Meds", "meds", 5, "high", recurrence="daily")
    pet.add_task(meds)

    following = pet.complete_task(meds, today=today)

    assert meds.status == "completed"
    assert following is not None
    assert following is not meds  # a genuinely new instance
    assert following.status == "pending"
    assert following.due_date == today + timedelta(days=1)
    assert len(pet.tasks) == 2  # completed original + next occurrence


def test_completing_weekly_task_spawns_seven_days_later():
    """A completed weekly task's next instance is due seven days out."""
    today = date(2026, 7, 7)
    pet = Pet("Biscuit", "dog", 3)
    bath = Task("Bath", "grooming", 30, "medium", recurrence="weekly")
    pet.add_task(bath)

    following = pet.complete_task(bath, today=today)

    assert following.due_date == today + timedelta(days=7)


def test_completing_one_shot_task_spawns_nothing():
    """A non-recurring task just completes; no new instance appears."""
    today = date(2026, 7, 7)
    pet = Pet("Biscuit", "dog", 3)
    walk = Task("Walk", "walk", 30, "high")
    pet.add_task(walk)

    following = pet.complete_task(walk, today=today)

    assert following is None
    assert walk.status == "completed"
    assert len(pet.tasks) == 1


def test_spawned_instance_not_due_until_its_date():
    """The next occurrence stays out of today's plan but is due on its day."""
    today = date(2026, 7, 7)
    pet = Pet("Milo", "cat", 5)
    meds = Task("Meds", "meds", 5, "high", recurrence="daily")
    pet.add_task(meds)

    following = pet.complete_task(meds, today=today)

    assert not following.is_due(today)
    assert following.is_due(today + timedelta(days=1))


def test_generate_plan_includes_due_recurring_task():
    """A recurring task due today lands in the generated plan."""
    pet = Pet("Milo", "cat", 5)
    pet.add_task(Task("Meds", "meds", 5, "high", recurrence="daily"))
    owner = Owner("Sarah", [pet])
    scheduler = Scheduler(owner, 90)

    scheduler.generate_plan(today=date(2026, 7, 7))

    assert [e.task.description for e in scheduler.plan] == ["Meds"]


def test_generate_plan_orders_entries_chronologically():
    """The generated plan lists tasks in ascending start time, regardless of
    the order they were added or picked."""
    pet = Pet("Biscuit", "dog", 3)
    pet.add_task(Task("Walk", "walk", 30, "high", preferred_time="09:00"))
    pet.add_task(Task("Meds", "meds", 10, "high", preferred_time="08:00"))
    scheduler = Scheduler(Owner("Sarah", [pet]), 120)

    scheduler.generate_plan(today=date(2026, 7, 7))

    starts = [e.start_time for e in scheduler.plan]
    assert starts == sorted(starts)  # chronological, earliest first
    assert starts[0] == "08:00"


def test_detect_conflicts_flags_identical_times():
    """Two tasks pinned to the exact same time clash (one owner, one place)."""
    dog = Pet("Biscuit", "dog", 3)
    dog.add_task(Task("Walk", "walk", 30, "high", preferred_time="08:00"))
    cat = Pet("Milo", "cat", 5)
    cat.add_task(Task("Meds", "meds", 10, "high", preferred_time="08:00"))
    scheduler = Scheduler(Owner("Sarah", [dog, cat]), 120)
    scheduler.generate_plan(today=date(2026, 7, 7))

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "overlaps" in conflicts[0]


def test_detect_conflicts_flags_overlapping_fixed_times():
    """Two fixed-time tasks whose windows overlap produce one warning."""
    dog = Pet("Biscuit", "dog", 3)
    dog.add_task(Task("Walk", "walk", 30, "high", preferred_time="08:00"))
    cat = Pet("Milo", "cat", 5)
    cat.add_task(Task("Meds", "meds", 10, "high", preferred_time="08:15"))
    scheduler = Scheduler(Owner("Sarah", [dog, cat]), 120)
    scheduler.generate_plan(today=date(2026, 7, 7))

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "overlaps" in conflicts[0]


def test_detect_conflicts_empty_when_times_dont_overlap():
    """Back-to-back fixed times (touching but not overlapping) don't clash."""
    dog = Pet("Biscuit", "dog", 3)
    dog.add_task(Task("Walk", "walk", 30, "high", preferred_time="08:00"))
    dog.add_task(Task("Feed", "feeding", 10, "high", preferred_time="08:30"))
    scheduler = Scheduler(Owner("Sarah", [dog]), 120)
    scheduler.generate_plan(today=date(2026, 7, 7))

    assert scheduler.detect_conflicts() == []


def test_invalid_fixed_time_falls_back_to_flexible_without_crashing():
    """A malformed preferred_time is treated as flexible, not a crash."""
    pet = Pet("Biscuit", "dog", 3)
    pet.add_task(Task("Walk", "walk", 30, "high", preferred_time="not a time"))
    scheduler = Scheduler(Owner("Sarah", [pet]), 90)

    scheduler.generate_plan(today=date(2026, 7, 7))  # must not raise

    # Placed flexibly at the start of the day, and no false conflict.
    assert scheduler.plan[0].start_time == "08:00"
    assert scheduler.detect_conflicts() == []
