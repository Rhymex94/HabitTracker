from collections import defaultdict
from flask import Blueprint, jsonify, request
from app.auth import token_required
from app.models import ProgressEntry
from app.redis_client import get_cached_streak, set_cached_streak
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
        ProgressEntry.query.filter(
            ProgressEntry.habit_id.in_(habit_dict.keys())
        )
        .order_by(ProgressEntry.date.desc())
        .all()
    )

    # Group progress entries by habit_id
    grouped_entries = defaultdict(list)
    for entry in progress_entries:
        grouped_entries[entry.habit_id].append(entry)

    # Assign grouped entries to habit_dict
    for habit_id in habit_dict.keys():
        habit_dict[habit_id]["progress_entries"] = grouped_entries[habit_id]

    for habit_obj in habit_dict.values():
        habit = habit_obj["habit"]

        # Check cache first
        cached_streak = get_cached_streak(habit.id)
        if cached_streak is not None:
            streaks[habit.id] = cached_streak
            continue

        # Cache miss - calculate and cache
        entries = habit_obj["progress_entries"]
        streak = calculate_streak(habit, entries)
        set_cached_streak(habit.id, streak)
        streaks[habit.id] = streak

    return jsonify(streaks)
