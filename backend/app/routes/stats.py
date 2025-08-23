from flask import Blueprint, jsonify, request
from app.auth import token_required
from app.enums import HabitFrequency, HabitType
from app.models import db, Habit, ProgressEntry
from datetime import date, timedelta

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")

# Utility functions


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
    current_range_value = 0

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

# Endpoints


@stats_bp.route("", methods=["GET"])
@token_required
def get_stats():
    streaks = {}

    # TODO: Getting a habit_dict of all habits is probably a common pattern.
    #   Consider creating a utility function of this instead.
    habits = Habit.query.filter_by(user_id=request.user_id).all()
    habit_dict = {}
    for habit in habits:
        habit_dict[habit.id] = {"habit": habit, "progress_entries": []}

    progress_entries = (
        db.session.query(ProgressEntry.habit_id, ProgressEntry.date, ProgressEntry.value)
        .filter(ProgressEntry.habit_id.in_([habit.id for habit in habits]))
        .order_by(ProgressEntry.habit_id, ProgressEntry.date.desc())
        .all()
    )


    current_habit = None
    habit_index = None
    for i in range(0, len(progress_entries)):
        entry = progress_entries[i]
        if current_habit is None:
            current_habit = entry.habit_id
            habit_index = i

        if current_habit != entry.habit_id:
            habit_dict[current_habit]["progress_entries"] = progress_entries[habit_index:i]
            habit_index = i
            current_habit = entry.habit_id
    
    habit_dict[current_habit]["progress_entries"] = progress_entries[habit_index:]

    for habit_obj in habit_dict.values():
        habit = habit_obj["habit"]
        entries = habit_obj["progress_entries"]
        streaks[habit.id] = calculate_streak(habit, entries)

    return jsonify(streaks)
