from flask import Blueprint, request, jsonify
from app.models import db, Habit
from app.enums import HabitFrequency, HabitType
from app.auth import token_required

habits_bp = Blueprint("habits", __name__, url_prefix="/habits")


@habits_bp.route("", methods=["POST"])
@token_required
def create_habit():
    data = request.get_json()
    name = data.get("name")
    type_ = data.get("type")
    frequency_ = data.get("frequency")
    target_value = data.get("target")

    if not all([name, type_, target_value]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        habit_type = HabitType[type_.upper()]
        frequency = HabitFrequency[frequency_.upper()]
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid type or frequency value"}), 400

    new_habit = Habit(
        name=name,
        type=habit_type,
        frequency=frequency,
        target_value=target_value,
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
            }
        ),
        201,
    )


@habits_bp.route("", methods=["GET"])
@token_required
def fetch_habits():
    habits = Habit.query.filter_by(user_id=request.user_id).all()

    return (
        jsonify(
            [
                {
                    "id": habit.id,
                    "name": habit.name,
                    "type": habit.type.name.lower(),
                    "frequency": habit.frequency.name.lower(),
                    "target": habit.target_value,
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
