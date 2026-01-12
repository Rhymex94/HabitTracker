from datetime import date
from flask import Blueprint, request, jsonify
from app.models import db, Habit, ProgressEntry
from app.enums import HabitFrequency, HabitType
from app.auth import token_required
from app.utils import get_date_range, calculate_habit_completion
from app.validators import validate_habit_data

habits_bp = Blueprint("habits", __name__, url_prefix="/habits")


@habits_bp.route("", methods=["POST"])
@token_required
def create_habit():
    data = request.get_json()
    name = data.get("name")
    type_ = data.get("type")
    frequency_ = data.get("frequency")
    target_value = data.get("target")
    unit = data.get("unit")

    # Validate input data
    is_valid, error_message = validate_habit_data(data, is_update=False)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Validate other required fields
    if not type_ or target_value is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        habit_type = HabitType[type_.upper()]
        frequency = HabitFrequency[frequency_.upper()]
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid type or frequency value"}), 400

    if habit_type == HabitType.ABOVE and target_value == 0:
        return (
            jsonify(
                {"error": "Above -type habits must have a target value higher than 0."}
            ),
            400,
        )

    new_habit = Habit(
        name=name,
        type=habit_type,
        frequency=frequency,
        target_value=target_value,
        unit=unit,
        user_id=request.user_id,
    )

    db.session.add(new_habit)
    db.session.commit()

    return (
        jsonify(
            {
                "id": new_habit.id,
                "name": new_habit.name,
                "type": new_habit.type.name.lower(),
                "frequency": new_habit.frequency.name.lower(),
                "target": new_habit.target_value,
                "unit": new_habit.unit,
            }
        ),
        201,
    )


@habits_bp.route("/<int:habit_id>", methods=["PATCH"])
@token_required
def update_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()

    if not habit:
        return jsonify({"error": "Habit not found"}), 404
    data = request.get_json()

    # Validate input data
    is_valid, error_message = validate_habit_data(data, is_update=True)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Whitelist of allowed fields to prevent attribute injection
    allowed_fields = {"name", "type", "frequency", "target_value", "unit"}

    for key, value in data.items():
        # Map "target" to "target_value" for backwards compatibility
        if key == "target":
            key = "target_value"

        # Only set whitelisted attributes
        if key in allowed_fields:
            setattr(habit, key, value)

    db.session.commit()

    return jsonify({"message": "Habit updated successfully."}), 200


@habits_bp.route("", methods=["GET"])
@token_required
def fetch_habits():
    habits = Habit.query.filter_by(user_id=request.user_id).all()
    today = date.today()

    # Return early if no habits
    if not habits:
        return jsonify([]), 200

    # Calculate date ranges for each habit
    habit_date_ranges = {}
    for habit in habits:
        start_date, end_date = get_date_range(today, habit.frequency)
        habit_date_ranges[habit.id] = (start_date, end_date)

    # Fetch ALL progress entries for ALL habits in a single query
    habit_ids = [habit.id for habit in habits]
    all_progress_entries = (
        ProgressEntry.query.filter(ProgressEntry.habit_id.in_(habit_ids)).all()
    )

    # Group progress entries by habit_id and filter by date range
    habit_progress = {habit_id: [] for habit_id in habit_ids}
    for entry in all_progress_entries:
        start_date, end_date = habit_date_ranges[entry.habit_id]
        if start_date <= entry.date < end_date:
            habit_progress[entry.habit_id].append(entry)

    return (
        jsonify(
            [
                {
                    "id": habit.id,
                    "name": habit.name,
                    "type": habit.type.name.lower(),
                    "frequency": habit.frequency.name.lower(),
                    "target": habit.target_value,
                    "unit": habit.unit,
                    "is_completed": calculate_habit_completion(
                        habit, habit_progress[habit.id]
                    ),
                }
                for habit in habits
            ]
        ),
        200,
    )


@habits_bp.route("/<int:habit_id>", methods=["DELETE"])
@token_required
def delete_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    db.session.delete(habit)
    db.session.commit()

    return jsonify({"message": "Habit deleted successfully."}), 200
