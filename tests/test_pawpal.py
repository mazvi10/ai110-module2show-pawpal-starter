"""Tests for the PawPal+ core system."""

from pawpal_system import Pet, Task


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
