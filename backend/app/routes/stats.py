from collections import defaultdict
from flask import Blueprint, jsonify, request
from app.auth import token_required
from app.models import Habit, ProgressEntry
from app.redis_client import get_cached_streak, set_cached_streak
from app.utils import calculate_streak

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("", methods=["GET"])
@token_required
def get_stats():
    streaks = {}

    habits = Habit.query.filter_by(user_id=request.user_id).all()
    if not habits:
        return jsonify({"success": True, "data": streaks})

    habit_ids = [habit.id for habit in habits]

    progress_entries = (
        ProgressEntry.query.filter(ProgressEntry.habit_id.in_(habit_ids))
        .order_by(ProgressEntry.date.desc())
        .all()
    )

    # Group progress entries by habit_id
    grouped_entries = defaultdict(list)
    for entry in progress_entries:
        grouped_entries[entry.habit_id].append(entry)

    for habit in habits:
        # Check cache first
        cached_streak = get_cached_streak(habit.id)
        if cached_streak is not None:
            streaks[habit.id] = cached_streak
            continue

        # Cache miss - calculate and cache
        entries = grouped_entries[habit.id]
        streak = calculate_streak(habit, entries)
        set_cached_streak(habit.id, streak)
        streaks[habit.id] = streak

    return jsonify({"success": True, "data": streaks})
