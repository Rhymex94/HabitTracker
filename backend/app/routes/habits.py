from flask import Blueprint, request, jsonify
from app.models import db, Habit, ProgressEntry
from app.enums import HabitFrequency, HabitType
from app.auth import token_required
from app.utils import filter_progress_to_current_period, calculate_habit_completion
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
        return jsonify({"success": False, "message": error_message}), 400

    # Validate other required fields
    if not type_ or target_value is None:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        habit_type = HabitType[type_.upper()]
        frequency = HabitFrequency[frequency_.upper()]
    except (KeyError, ValueError):
        return jsonify({"success": False, "message": "Invalid type or frequency value"}), 400

    if habit_type == HabitType.ABOVE and target_value == 0:
        return (
            jsonify(
                {"success": False, "message": "Above -type habits must have a target value higher than 0."}
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
        jsonify({
            "success": True,
            "data": {
                "id": new_habit.id,
                "name": new_habit.name,
                "type": new_habit.type.name.lower(),
                "frequency": new_habit.frequency.name.lower(),
                "target": new_habit.target_value,
                "unit": new_habit.unit,
            },
        }),
        201,
    )


@habits_bp.route("/<int:habit_id>", methods=["PATCH"])
@token_required
def update_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()

    if not habit:
        return jsonify({"success": False, "message": "Habit not found"}), 404
    data = request.get_json()

    # Validate input data
    is_valid, error_message = validate_habit_data(data, is_update=True)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400

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

    return jsonify({"success": True, "message": "Habit updated successfully."}), 200


@habits_bp.route("", methods=["GET"])
@token_required
def fetch_habits():
    habits = Habit.query.filter_by(user_id=request.user_id).all()

    # Return early if no habits
    if not habits:
        return jsonify({"success": True, "data": []}), 200

    # Fetch ALL progress entries for ALL habits in a single query
    habit_ids = [habit.id for habit in habits]
    all_progress_entries = (
        ProgressEntry.query.filter(ProgressEntry.habit_id.in_(habit_ids)).all()
    )

    # Filter progress entries to current period for each habit
    habit_progress = filter_progress_to_current_period(habits, all_progress_entries)

    return (
        jsonify({
            "success": True,
            "data": [
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
            ],
        }),
        200,
    )


@habits_bp.route("/<int:habit_id>", methods=["DELETE"])
@token_required
def delete_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=request.user_id).first()

    if not habit:
        return jsonify({"success": False, "message": "Habit not found"}), 404

    db.session.delete(habit)
    db.session.commit()

    return jsonify({"success": True, "message": "Habit deleted successfully."}), 200
