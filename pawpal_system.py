"""PawPal+ core system.

Implements the four core classes from diagrams/uml_draft.mmd:
Task, Pet, Owner, and the Scheduler that plans tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# Lower rank = more urgent. Unknown priorities sort last.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# Task status values (defined once so filters can't drift on a typo).
PENDING = "pending"
COMPLETED = "completed"

# How far ahead each recurrence schedules its next occurrence. Using timedelta
# keeps month/year rollovers correct (e.g. Jul 31 + 1 day -> Aug 1).
RECURRENCE_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
}

# The plan lays tasks out starting from this time of day.
DAY_START_MINUTES = 8 * 60  # 08:00


def _priority_rank(priority: str) -> int:
    """Map a priority label to a sort rank (lower = more urgent)."""
    return PRIORITY_RANK.get(priority.lower(), len(PRIORITY_RANK))


def _minutes_to_clock(minutes: int) -> str:
    """Turn a minute-of-day count into an 'HH:MM' string."""
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


def _clock_to_minutes(clock: str | None) -> int | None:
    """Turn an 'HH:MM' string into a minute-of-day count.

    Lenient by design: returns None for anything that isn't a valid 24-hour
    time (including None or junk) so callers can treat a bad time as "no fixed
    time" instead of crashing the plan.
    """
    if not clock:
        return None
    hours_str, sep, mins_str = clock.strip().partition(":")
    if not sep or not hours_str.isdigit() or not mins_str.isdigit():
        return None
    hours, mins = int(hours_str), int(mins_str)
    if not (0 <= hours < 24 and 0 <= mins < 60):
        return None
    return hours * 60 + mins


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, enrichment, etc.)."""

    description: str
    category: str
    duration: int  # minutes ("time")
    priority: str
    status: str = PENDING
    # "daily" / "weekly" repeat automatically; None is a one-shot task.
    recurrence: str | None = None
    # The day this instance is scheduled for. None means "due whenever" (the
    # first occurrence of a task, before it has been scheduled ahead).
    due_date: date | None = None
    # Fixed "HH:MM" start (e.g. meds at a set time); None means flexible.
    preferred_time: str | None = None

    def is_due(self, today: date) -> bool:
        """Whether this task should appear in the plan for ``today``: it must
        be pending and either have no scheduled date or be scheduled on/before
        today (a future occurrence stays out until its day arrives)."""
        if self.status == COMPLETED:
            return False
        return self.due_date is None or self.due_date <= today

    def mark_complete(self) -> None:
        """Mark this task as done so it's excluded from future plans. Spawning
        the next occurrence of a recurring task is handled by
        ``Pet.complete_task``, which owns the task list."""
        self.status = COMPLETED

    def next_occurrence(self, today: date | None = None) -> "Task | None":
        """Return a fresh, pending Task for this task's next occurrence, or
        None if it doesn't recur. The new instance is due ``today`` plus this
        recurrence's interval (daily -> +1 day, weekly -> +7 days)."""
        delta = RECURRENCE_DELTAS.get(self.recurrence or "")
        if delta is None:
            return None
        today = today or date.today()
        return Task(
            self.description,
            self.category,
            self.duration,
            self.priority,
            recurrence=self.recurrence,
            due_date=today + delta,
            preferred_time=self.preferred_time,
        )


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

    def complete_task(self, task: Task, today: date | None = None) -> Task | None:
        """Mark ``task`` complete and, if it recurs, automatically add a fresh
        instance for its next occurrence to this pet. Returns the new instance
        (or None for a one-shot task).

        This is the completion entry point for recurring tasks: it keeps the
        finished instance as history and schedules the follow-up so the task
        reappears on its next due date."""
        today = today or date.today()
        task.mark_complete()
        following = task.next_occurrence(today)
        if following is not None:
            self.add_task(following)
        return following

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
    start_minutes: int = -1  # minute-of-day of start_time, for sorting/overlap


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

    def filter_tasks(
        self,
        pet: Pet | None = None,
        status: str | None = PENDING,
        category: str | None = None,
        due_on: date | None = None,
    ) -> list[Task]:
        """Return the owner's tasks narrowed by pet, status, and/or category.

        Single source of truth for "which tasks are we looking at": every
        argument left as its default widens the selection. Passing
        ``status=None`` includes completed tasks. When ``due_on`` is given,
        temporal eligibility (``Task.is_due``) replaces the status filter, so
        recurring tasks that are due again reappear and ones already done for
        that day drop out. Results are not sorted; callers that care about
        order use ``sort_by_priority``.
        """
        pets = [pet] if pet is not None else self.owner.pet_list

        def keep(task: Task) -> bool:
            if due_on is not None:
                if not task.is_due(due_on):
                    return False
            elif status is not None and task.status != status:
                return False
            return category is None or task.category == category

        return [task for p in pets for task in p.tasks if keep(task)]

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered by priority (high first), then by shortest
        duration so equal-priority tasks pack more efficiently. Stable beyond
        that: tasks tied on both keep their original order."""
        return sorted(
            tasks,
            key=lambda task: (_priority_rank(task.priority), task.duration),
        )

    def get_single_pet_tasks(self, pet: Pet) -> list[Task]:
        """Return the pending tasks belonging to a single pet, in priority
        order. Useful for a per-pet view in the UI."""
        return self.sort_by_priority(self.filter_tasks(pet=pet))

    def generate_plan(self, today: date | None = None) -> list[PlanEntry]:
        """Pool the tasks due on ``today`` from all of the owner's pets, sort
        by priority, and greedily fit them within time_available. Tasks that
        fit get a clock start_time; the rest go to self.skipped. Recurring
        tasks are included on their cycle. Returns self.plan."""
        today = today or date.today()
        # Pool tasks across pets while remembering which pet each belongs to.
        entries = [
            PlanEntry(pet=pet, task=task)
            for pet in self.owner.pet_list
            for task in self.filter_tasks(pet=pet, due_on=today)
        ]
        entries.sort(
            key=lambda entry: (
                _priority_rank(entry.task.priority),
                entry.task.duration,
            )
        )

        self.plan = []
        self.skipped = []
        current_time = DAY_START_MINUTES
        remaining = self.time_available

        for entry in entries:
            if entry.task.duration <= remaining:
                fixed = _clock_to_minutes(entry.task.preferred_time)
                if fixed is not None:
                    # Fixed appointment: pin it to its requested time. We don't
                    # advance the cursor, so flexible tasks keep filling from
                    # where they were — any resulting clash is reported by
                    # detect_conflicts() rather than silently reshuffled. A
                    # blank or malformed time parses to None and falls through
                    # to flexible placement instead of crashing.
                    start = fixed
                else:
                    start = current_time
                    current_time += entry.task.duration
                entry.start_minutes = start
                entry.start_time = _minutes_to_clock(start)
                remaining -= entry.task.duration
                self.plan.append(entry)
            else:
                self.skipped.append(entry)

        # Present the day in chronological order regardless of pick order.
        self.plan.sort(key=lambda entry: entry.start_minutes)
        return self.plan

    def detect_conflicts(self) -> list[str]:
        """Return a warning message for each pair of planned tasks whose time
        windows overlap. Empty list means no clashes.

        Lightweight and non-crashing: it only reads times already placed on
        the plan, and the owner can only be in one place at a time, so any two
        tasks sharing a minute clash — usually two fixed-time tasks, or a fixed
        task landing on a flexible one. Assumes self.plan is sorted by
        start_minutes (generate_plan leaves it that way)."""
        warnings: list[str] = []
        for i, first in enumerate(self.plan):
            first_end = first.start_minutes + first.task.duration
            for second in self.plan[i + 1:]:
                # Sorted by start, so once one starts at/after first ends,
                # nothing later can overlap first either.
                if second.start_minutes >= first_end:
                    break
                warnings.append(
                    f"{first.pet.name}'s {first.task.description} "
                    f"({first.start_time}) overlaps {second.pet.name}'s "
                    f"{second.task.description} ({second.start_time})."
                )
        return warnings

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

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("Conflicts:")
            lines.extend(f"  ⚠ {warning}" for warning in conflicts)
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
