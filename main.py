"""PawPal+ demo script

Exercises the scheduler's sorting, filtering, and conflict-detection logic in
the terminal so you can eyeball that each behaves as expected.
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def _rule(title: str) -> None:
    """Print a titled section divider."""
    print("=" * 48)
    print(title)
    print("=" * 48)


def _task_line(task: Task) -> str:
    """One readable line describing a task."""
    return (
        f"  {task.description} ({task.duration} min, {task.priority} priority,"
        f" {task.category})"
    )


def build_demo_owner() -> Owner:
    """Create a sample owner whose tasks are deliberately added OUT OF ORDER
    (mixed priorities and durations, plus one already-completed task) so the
    sorting and filtering methods have something real to prove."""
    biscuit = Pet("Biscuit", "Golden Retriever", 3)
    # Note the order: low first, then a long high, then a short high.
    biscuit.add_task(Task("Grooming", "grooming", 40, "low"))
    biscuit.add_task(Task("Morning walk", "walk", 30, "high"))
    biscuit.add_task(Task("Feeding", "feeding", 10, "high"))
    # An already-done task, to show filtering leaves it out of the plan.
    done = Task("Early potty break", "walk", 5, "high")
    done.mark_complete()
    biscuit.add_task(done)

    milo = Pet("Milo", "Cat", 5)
    milo.add_task(Task("Play time", "enrichment", 20, "medium"))
    milo.add_task(Task("Give meds", "meds", 5, "high"))

    return Owner("Sarah", [biscuit, milo])


def demo_sorting_and_filtering(owner: Owner) -> None:
    """Show sort_by_priority and filter_tasks working on out-of-order input."""
    scheduler = Scheduler(owner, time_available=90)

    _rule("Sorting: pending tasks, high-priority & shortest-first")
    pending = scheduler.filter_tasks()  # all pending, across every pet
    for task in scheduler.sort_by_priority(pending):
        print(_task_line(task))
    print("  ^ Feeding (10 min) sorts before Morning walk (30 min): same")
    print("    priority, shorter duration wins the tie.")
    print()

    _rule("Filtering: by pet, by status, by category")
    milo = owner.pet_list[1]
    print("Milo's pending tasks:")
    for task in scheduler.filter_tasks(pet=milo):
        print(_task_line(task))

    print("\nCompleted tasks (excluded from plans):")
    for task in scheduler.filter_tasks(status="completed"):
        print(_task_line(task))

    print("\nOnly 'walk' tasks that are still pending:")
    for task in scheduler.filter_tasks(category="walk"):
        print(_task_line(task))
    print()


def demo_schedule(owner: Owner) -> None:
    """Build and print the day's plan for the demo owner."""
    scheduler = Scheduler(owner, time_available=90)
    scheduler.generate_plan()

    _rule("Today's Schedule")
    print(scheduler.format_schedule())
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())
    print()


def demo_conflict() -> None:
    """Add two tasks pinned to the SAME time and confirm the scheduler both
    detects the clash and prints a warning."""
    biscuit = Pet("Biscuit", "Golden Retriever", 3)
    biscuit.add_task(Task("Morning walk", "walk", 30, "high", preferred_time="08:00"))

    milo = Pet("Milo", "Cat", 5)
    # Same 08:00 start as Biscuit's walk — one owner can't do both at once.
    milo.add_task(Task("Give meds", "meds", 10, "high", preferred_time="08:00"))

    scheduler = Scheduler(Owner("Sarah", [biscuit, milo]), time_available=90)
    scheduler.generate_plan()

    _rule("Conflict detection: two tasks at 08:00")
    print(scheduler.format_schedule())
    print()

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print(f"⚠ Scheduler found {len(conflicts)} conflict(s):")
        for warning in conflicts:
            print(f"  - {warning}")
    else:
        print("No conflicts detected (unexpected!).")
    print()


def demo_recurrence() -> None:
    """Complete a daily and a weekly task and show that each automatically
    spawns a fresh instance for its next occurrence."""
    today = date(2026, 7, 7)
    milo = Pet("Milo", "Cat", 5)
    meds = Task("Give meds", "meds", 5, "high", recurrence="daily")
    bath = Task("Bath", "grooming", 30, "medium", recurrence="weekly")
    milo.add_task(meds)
    milo.add_task(bath)

    _rule(f"Recurrence: completing tasks on {today}")
    for task in (meds, bath):
        following = milo.complete_task(task, today=today)
        print(
            f"Completed '{task.description}' ({task.recurrence}) -> "
            f"status now '{task.status}'."
        )
        print(f"  Next '{following.description}' auto-scheduled for "
              f"{following.due_date} (was {today}).")
    print()
    print("Milo's task list now (completed originals + next occurrences):")
    for task in milo.tasks:
        due = task.due_date or "—"
        print(f"  {task.description}: status={task.status}, due={due}")
    print()


def main() -> None:
    owner = build_demo_owner()
    demo_sorting_and_filtering(owner)
    demo_schedule(owner)
    demo_conflict()
    demo_recurrence()


if __name__ == "__main__":
    main()
