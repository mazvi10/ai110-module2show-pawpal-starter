"""PawPal+ demo script
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and several tasks."""
    biscuit = Pet("Biscuit", "Golden Retriever", 3)
    biscuit.add_task(Task("Morning walk", "walk", 30, "high"))
    biscuit.add_task(Task("Feeding", "feeding", 10, "high"))
    biscuit.add_task(Task("Grooming", "grooming", 40, "low"))

    milo = Pet("Milo", "Cat", 5)
    milo.add_task(Task("Give meds", "meds", 5, "high"))
    milo.add_task(Task("Play time", "enrichment", 20, "medium"))

    return Owner("Sarah", [biscuit, milo])


def main() -> None:
    owner = build_demo_owner()

    # 90 minutes of care time available today.
    scheduler = Scheduler(owner, time_available=90)
    scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.format_schedule())
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
