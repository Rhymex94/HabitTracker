from flask import Blueprint, jsonify, request
from app.auth import token_required
from app.models import db, Habit, ProgressEntry
from app.utils import calculate_streak, get_habit_dict

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("", methods=["GET"])
@token_required
def get_stats():
    streaks = {}

    # TODO: Getting a habit_dict of all habits is probably a common pattern.
    #   Consider creating a utility function of this instead.
    habit_dict = get_habit_dict(request.user_id)

    progress_entries = (
        db.session.query(ProgressEntry.habit_id, ProgressEntry.date, ProgressEntry.value)
        .filter(ProgressEntry.habit_id.in_([habit_id for habit_id in habit_dict.keys()]))
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
