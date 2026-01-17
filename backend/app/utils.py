from datetime import date, timedelta
from typing import Sequence

from app.enums import HabitFrequency, HabitType
from app.models import Habit, ProgressEntry


def filter_progress_to_current_period(
    habits: Sequence[Habit],
    progress_entries: Sequence[ProgressEntry],
    reference_date: date | None = None,
) -> dict[int, list[ProgressEntry]]:
    """
    Filter progress entries to the current period for each habit.

    Args:
        habits: List of Habit objects (need id and frequency)
        progress_entries: List of ProgressEntry objects to filter
        reference_date: The reference date for calculating periods (defaults to today)

    Returns:
        Dictionary mapping habit_id to list of ProgressEntry objects
        that fall within the habit's current period.
        Uses exclusive end date (start <= entry.date < end).
    """
    if reference_date is None:
        reference_date = date.today()

    # Calculate date ranges for each habit
    habit_date_ranges = {}
    for habit in habits:
        start_date, end_date = get_date_range(reference_date, habit.frequency)
        habit_date_ranges[habit.id] = (start_date, end_date)

    # Initialize result with empty lists for each habit
    result: dict[int, list[ProgressEntry]] = {habit.id: [] for habit in habits}

    # Filter entries by date range
    for entry in progress_entries:
        if entry.habit_id in habit_date_ranges:
            start_date, end_date = habit_date_ranges[entry.habit_id]
            # Exclusive end date: start <= date < end
            if start_date <= entry.date < end_date:
                result[entry.habit_id].append(entry)

    return result


def get_date_range(current_date: date, frequency: HabitFrequency) -> tuple[date, date]:

    # Returns a range matching the frequency.
    # Start is inclusive, end is exclusive.

    match frequency:
        case HabitFrequency.DAILY:
            start = current_date
            end = current_date + timedelta(days=1)
        case HabitFrequency.WEEKLY:
            start = current_date - timedelta(days=current_date.weekday())
            end = start + timedelta(days=7)
        case HabitFrequency.MONTHLY:
            start = date(current_date.year, current_date.month, 1)
            if current_date.month == 12:
                end = date(current_date.year + 1, 1, 1)
            else:
                end = date(current_date.year, current_date.month + 1, 1)
        case HabitFrequency.YEARLY:
            start = date(current_date.year, 1, 1)
            end = date(current_date.year + 1, 1, 1)
    return start, end


def calculate_habit_completion(habit: Habit, progress_entries: list[ProgressEntry]) -> bool:
    """
    Calculate if a habit is completed for the current period.

    Args:
        habit: The Habit object
        progress_entries: List of ProgressEntry objects for the current period

    Returns:
        bool: True if the habit is completed, False otherwise
    """
    total_progress = sum(entry.value for entry in progress_entries)

    if habit.type == HabitType.ABOVE:
        return total_progress >= habit.target_value
    elif habit.type == HabitType.BELOW:
        return total_progress <= habit.target_value
    else:
        raise ValueError(f"Unknown habit type {habit.type}")


def calculate_streak(habit: Habit, progress: list[ProgressEntry]) -> int:
    # Assumes the ProgressEntry list in reverse order: from newest to oldest.
    streak = 0

    today = date.today()
    present_start, _ = get_date_range(today, habit.frequency)

    current_range_start = present_start

    progress_by_period = {}
    progress_by_period[current_range_start] = 0

    start_date_period, _ = get_date_range(habit.start_date, habit.frequency)

    for entry in progress:
        period_start, _ = get_date_range(entry.date, habit.frequency)
        progress_by_period.setdefault(period_start, 0)
        progress_by_period[period_start] += entry.value

    while current_range_start >= start_date_period:
        current_value = progress_by_period.get(current_range_start, 0)

        if habit.type == HabitType.ABOVE:
            success = current_value >= habit.target_value
        elif habit.type == HabitType.BELOW:
            success = current_value <= habit.target_value
        else:
            raise ValueError(f"Unknown habit type {habit.type}")

        if not success and current_range_start != present_start:
            break

        if success:
            streak += 1
        else:
            # Not successful in the present period (but it's still onging).
            pass

        # Move backwards one period.
        current_range_start, _ = get_date_range(
            current_range_start - timedelta(days=1), habit.frequency
        )
    
    return streak