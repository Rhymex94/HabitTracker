from flask import Blueprint, request, jsonify, current_app
import datetime
from sqlalchemy.exc import IntegrityError

from app.models import db, Habit, ProgressEntry


progress_bp = Blueprint("progress", __name__)


@progress_bp.route("/progress", methods=["POST"])
def add_progress():
    data = request.get_json()
    habit_id = data.get("habit_id")
    date_str = data.get("date")
    value = data.get("value")

    if not habit_id or value is None:
        return jsonify({"error": "Missing required fields"}), 400

    habit = db.session.get(Habit, habit_id)
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    try:
        entry_date = (
            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else datetime.utcnow().date()
        )
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Validate value according to habit type
    if habit.type.name == "BINARY":
        if value not in [0, 1]:
            return jsonify({"error": "Binary habits must have value 0 or 1"}), 400
    elif habit.type.name == "QUANTITATIVE":
        if not isinstance(value, int) or value < 0:
            return (
                jsonify(
                    {
                        "error": "Quantitative habits must have a non-negative integer value"
                    }
                ),
                400,
            )

    try:
        entry = ProgressEntry(habit_id=habit_id, date=entry_date, value=value)
        db.session.add(entry)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate entry for this habit and date"}), 400

    return (
        jsonify(
            {
                "id": entry.id,
                "habit_id": entry.habit_id,
                "date": entry.date.isoformat(),
                "value": entry.value,
            }
        ),
        201,
    )


@progress_bp.route("/progress", methods=["GET"])
def get_progress_entries():
    habit_id = request.args.get("habit_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = ProgressEntry.query

    if habit_id:
        query = query.filter_by(habit_id=habit_id)

    if start_date:
        try:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(ProgressEntry.date >= start_date_obj)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400

    if end_date:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(ProgressEntry.date <= end_date_obj)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    entries = query.all()
    return jsonify(
        [
            {
                "id": entry.id,
                "habit_id": entry.habit_id,
                "date": entry.date.isoformat(),
                "value": entry.value,
            }
            for entry in entries
        ]
    )


@progress_bp.route("/progress/<int:entry_id>", methods=["DELETE"])
def delete_progress_entry(entry_id):
    entry = db.session.get(ProgressEntry, entry_id)
    if not entry:
        return jsonify({"error": "Progress entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": f"Progress entry {entry_id} deleted"}), 200
