

from datetime import date, timedelta

from app.enums import HabitFrequency, HabitType
from app.models import Habit, ProgressEntry


def get_habit_dict(user_id: int):
    habits = Habit.query.filter_by(user_id=user_id).all()
    habit_dict = {}
    for habit in habits:
        habit_dict[habit.id] = {"habit": habit, "progress_entries": []}
    return habit_dict

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