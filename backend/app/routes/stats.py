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

    for entry in progress:
        if entry.date < current_range_start:
            # Outside of the range.

            if (
                current_range_value < habit.target_value
                and current_range_start != present_start
            ):
                # Did not reach the goal, and it's not the present range.
                return streak

            if current_range_value >= habit.target_value:
                streak += 1

            current_range_value = 0
            current_range_start, _ = get_date_range(
                current_range_start - timedelta(days=1), habit.frequency
            )

            # Sanity check: is the current entry at least within this next range?
            if entry.date < current_range_start:
                # If not, the streak ends here.
                return streak

        # Otherwise, we're within the period (could be the first in the new period).
        current_range_value += entry.value

    # Final check. In case the streak is unbroken from the beginning.
    if current_range_value >= habit.target_value:
        streak += 1

    return streak


# Endpoints


@stats_bp.route("", methods=["GET"])
@token_required
def get_stats():

    # TODO: Getting a habit_dict of all habits is probably a common pattern.
    #   Consider creating a utility function of this instead.
    habits = Habit.query.filter_by(user_id=request.user_id).all()
    habit_dict = {}
    for habit in habits:
        habit_dict[habit.id] = habit

    progress_entries = (
        db.session.query(ProgressEntry.habit_id, ProgressEntry.date, ProgressEntry.value)
        .filter(ProgressEntry.habit_id.in_([habit.id for habit in habits]))
        .order_by(ProgressEntry.habit_id, ProgressEntry.date.desc())
        .all()
    )

    streaks = {}

    current_habit = None
    habit_index = None

    # TODO: Would it be cleaner to just run through once, assign the indices to a dict,
    #   and call for each Habit?
    for i in range(0, len(progress_entries)):
        entry = progress_entries[i]
        if current_habit is None:
            current_habit = entry.habit_id
            habit_index = i

        if current_habit != entry.habit_id:
            streaks[current_habit] = calculate_streak(
                habit_dict[current_habit], progress_entries[habit_index:i]
            )
            habit_index = i
            current_habit = entry.habit_id

    # The last habit on the list never gets a chance to be called. Call it here, if it
    #   exists.
    if current_habit:
        streaks[current_habit] = calculate_streak(
            habit_dict[current_habit], progress_entries[habit_index:]
        )

    return jsonify(streaks)
