from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app.models import db, Habit, ProgressEntry
from app.auth import token_required
from app.redis_client import invalidate_streak_cache
from app.utils import filter_progress_to_current_period
from app.validators import validate_progress_data, validate_date_string

progress_bp = Blueprint("progress", __name__, url_prefix="/progress")


@progress_bp.route("", methods=["POST"])
@token_required
def add_progress():
    data = request.get_json()
    habit_id = data.get("habit_id")
    date_str = data.get("date")
    value = data.get("value")

    if not habit_id or value is None:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()
    if not habit:
        return jsonify({"success": False, "message": "Habit not found or unauthorized"}), 404

    # Validate date
    is_valid, error_message, entry_date = validate_date_string(date_str)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400

    # Use current date if no date provided
    if entry_date is None:
        entry_date = datetime.now(timezone.utc).date()

    # Validate progress value
    is_valid, error_message = validate_progress_data(data)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400

    try:
        entry = ProgressEntry(habit_id=habit_id, date=entry_date, value=value)
        db.session.add(entry)
        db.session.commit()
        invalidate_streak_cache(habit_id)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Duplicate entry for this habit and date"}), 400

    return (
        jsonify({
            "success": True,
            "data": {
                "id": entry.id,
                "habit_id": entry.habit_id,
                "date": entry.date.isoformat(),
                "value": entry.value,
            },
        }),
        201,
    )


@progress_bp.route("", methods=["GET"])
@token_required
def get_progress_entries():
    habit_id = request.args.get("habit_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    include_all = request.args.get("all", "false").lower() == "true"

    # First verify that the habit belongs to the user
    if habit_id:
        habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()
        if not habit:
            return jsonify({"success": False, "message": "Habit not found or unauthorized"}), 404

    query = ProgressEntry.query
    if habit_id:
        query = query.join(Habit).filter(
            Habit.user_id == request.user_id, ProgressEntry.habit_id == habit_id
        )
    else:
        query = query.join(Habit).filter(Habit.user_id == request.user_id)

    # Apply explicit date filters if given
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(ProgressEntry.date >= start_date_obj)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid start_date format. Use YYYY-MM-DD."}), 400

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(ProgressEntry.date <= end_date_obj)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    entries = query.all()
    if not include_all:
        habits = Habit.query.filter_by(user_id=request.user_id).all()
        filtered_by_habit = filter_progress_to_current_period(habits, entries)
        # Flatten the filtered results back into a list
        entries = [
            entry for entries_list in filtered_by_habit.values() for entry in entries_list
        ]

    return jsonify({
        "success": True,
        "data": [
            {
                "id": entry.id,
                "habit_id": entry.habit_id,
                "date": entry.date.isoformat(),
                "value": entry.value,
            }
            for entry in entries
        ],
    })


@progress_bp.route("/<int:entry_id>", methods=["DELETE"])
@token_required
def delete_progress_entry(entry_id):
    entry = db.session.get(ProgressEntry, entry_id)
    if not entry:
        return jsonify({"success": False, "message": "Progress entry not found"}), 404

    # Verify the progress entry's habit belongs to the authenticated user
    habit = Habit.query.filter_by(id=entry.habit_id, user_id=request.user_id).first()
    if not habit:
        return jsonify({"success": False, "message": "Progress entry not found"}), 404

    habit_id = entry.habit_id
    db.session.delete(entry)
    db.session.commit()
    invalidate_streak_cache(habit_id)
    return jsonify({"success": True, "message": f"Progress entry {entry_id} deleted"}), 200
