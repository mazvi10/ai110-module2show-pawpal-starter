"""PawPal+ core system.

Implements the four core classes from diagrams/uml_draft.mmd:
Task, Pet, Owner, and the Scheduler that plans tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Lower rank = more urgent. Unknown priorities sort last.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# The plan lays tasks out starting from this time of day.
DAY_START_MINUTES = 8 * 60  # 08:00


def _priority_rank(priority: str) -> int:
    """Map a priority label to a sort rank (lower = more urgent)."""
    return PRIORITY_RANK.get(priority.lower(), len(PRIORITY_RANK))


def _minutes_to_clock(minutes: int) -> str:
    """Turn a minute-of-day count into an 'HH:MM' string."""
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, enrichment, etc.)."""

    description: str
    category: str
    duration: int  # minutes ("time")
    priority: str
    status: str = "pending"

    def mark_complete(self) -> None:
        """Mark this task as done so it's excluded from future plans."""
        self.status = "completed"


@dataclass
class Pet:
    """A pet owned by the user, holding its own list of tasks."""

    name: str
    animal_type: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def delete_task(self, task: Task) -> None:
        """Remove a task from this pet (no error if it isn't present)."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """The pet owner, holding one or more pets."""

    name: str
    pet_list: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pet_list.append(pet)

    def delete_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (no error if it isn't present)."""
        if pet in self.pet_list:
            self.pet_list.remove(pet)


@dataclass
class PlanEntry:
    """One line in the daily plan: a task placed into today's schedule,
    together with the context the plan needs (which pet, and when)."""

    pet: Pet
    task: Task
    start_time: str = ""  # "HH:MM", assigned for included tasks


class Scheduler:
    """Builds a daily plan across all of the owner's pets.

    Reads the owner's pets directly (single source of truth) and stores the
    most recent plan on self, so explain/format don't recompute it.
    """

    def __init__(self, owner: Owner, time_available: int) -> None:
        self.owner = owner  # single source of truth for pets
        self.time_available = time_available  # minutes available today
        # Populated by generate_plan(); read by explain_plan()/format_schedule().
        self.plan: list[PlanEntry] = []
        self.skipped: list[PlanEntry] = []

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered by priority (high first). Stable: tasks
        of equal priority keep their original order."""
        return sorted(tasks, key=lambda task: _priority_rank(task.priority))

    def get_single_pet_tasks(self, pet: Pet) -> list[Task]:
        """Return the pending tasks belonging to a single pet, in priority
        order. Useful for a per-pet view in the UI."""
        pending = [task for task in pet.tasks if task.status != "completed"]
        return self.sort_by_priority(pending)

    def generate_plan(self) -> list[PlanEntry]:
        """Pool pending tasks from all of the owner's pets, sort by priority,
        and greedily fit them within time_available. Tasks that fit get a
        clock start_time; the rest go to self.skipped. Returns self.plan."""
        # Pool tasks across pets while remembering which pet each belongs to.
        entries = [
            PlanEntry(pet=pet, task=task)
            for pet in self.owner.pet_list
            for task in pet.tasks
            if task.status != "completed"
        ]
        entries.sort(key=lambda entry: _priority_rank(entry.task.priority))

        self.plan = []
        self.skipped = []
        current_time = DAY_START_MINUTES
        remaining = self.time_available

        for entry in entries:
            if entry.task.duration <= remaining:
                entry.start_time = _minutes_to_clock(current_time)
                current_time += entry.task.duration
                remaining -= entry.task.duration
                self.plan.append(entry)
            else:
                self.skipped.append(entry)

        return self.plan

    def explain_plan(self) -> str:
        """Return human-readable reasoning about which tasks were included or
        skipped and why, based on self.plan and self.skipped."""
        if not self.plan and not self.skipped:
            return "No tasks to plan — every task is either completed or unset."

        used = sum(entry.task.duration for entry in self.plan)
        lines = [
            f"Planned {len(self.plan)} task(s) using {used} of "
            f"{self.time_available} available minutes."
        ]
        for entry in self.plan:
            lines.append(
                f"  Included {entry.pet.name}'s {entry.task.description} "
                f"({entry.task.duration} min, {entry.task.priority} priority)."
            )
        for entry in self.skipped:
            lines.append(
                f"  Skipped {entry.pet.name}'s {entry.task.description} — "
                f"not enough time left (needs {entry.task.duration} min)."
            )
        return "\n".join(lines)

    def format_schedule(self) -> str:
        """Turn self.plan into readable text (usable by both the CLI and the
        Streamlit UI)."""
        if not self.plan:
            return "Daily plan: (nothing scheduled)"

        lines = [f"Daily plan for {self.owner.name}:"]
        for entry in self.plan:
            lines.append(
                f"  {entry.start_time} — {entry.pet.name}: "
                f"{entry.task.description} ({entry.task.duration} min) "
                f"[priority: {entry.task.priority}]"
            )
        return "\n".join(lines)
