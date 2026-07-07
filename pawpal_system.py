"""PawPal+ core system.

Class skeletons generated from diagrams/uml_draft.mmd.
No scheduling logic yet — just names, attributes, and empty method stubs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, enrichment, etc.)."""

    description: str
    category: str
    duration: int  # minutes
    priority: str
    status: str = "pending"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        ...


@dataclass
class Pet:
    """A pet owned by the user, holding its own list of tasks."""

    name: str
    animal_type: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        ...

    def delete_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        ...


@dataclass
class Owner:
    """The pet owner, holding one or more pets."""

    name: str
    pet_list: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        ...

    def delete_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        ...


@dataclass
class PlanEntry:
    """One line in the daily plan: a task placed into today's schedule,
    together with the context the plan needs (which pet, and when)."""

    pet: Pet
    task: Task
    start_time: str = ""  # optional, e.g. "08:00"


class Scheduler:
    """Builds a daily plan across all of the owner's pets.

    Not a dataclass: this class is behavior-first (it produces plans),
    so it's kept as a plain class to separate logic from the data objects.

    Reads the owner's pets directly (single source of truth) and stores
    the most recent plan on self, so explain/format don't recompute it.
    """

    def __init__(self, owner: Owner, time_available: int) -> None:
        self.owner = owner  # single source of truth for pets
        self.time_available = time_available  # minutes available today
        # Populated by generate_plan(); read by explain_plan()/format_schedule().
        self.plan: list[PlanEntry] = []
        self.skipped: list[PlanEntry] = []

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks ordered by priority."""
        ...

    def get_single_pet_tasks(self, pet: Pet) -> list[Task]:
        """Return the tasks belonging to a single pet."""
        ...

    def generate_plan(self) -> list[PlanEntry]:
        """Pool tasks from all of the owner's pets, sort by priority, and fit
        within time_available. Stores the result on self.plan (included) and
        self.skipped (didn't fit), and returns self.plan."""
        ...

    def explain_plan(self) -> str:
        """Return human-readable reasoning about which tasks were included or
        skipped and why, based on self.plan and self.skipped."""
        ...

    def format_schedule(self) -> str:
        """Turn self.plan into readable text (usable by both the CLI and the
        Streamlit UI)."""
        ...
