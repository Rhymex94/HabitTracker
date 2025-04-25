from flask import Blueprint, request, jsonify
from app.models import db, Habit, User
from app.enums import HabitFrequency, HabitType

habits_bp = Blueprint("habits", __name__, url_prefix="/habits")

@habits_bp.route("", methods=["POST"])
def create_habit():
    data = request.get_json()

    name = data.get("name")
    type_ = data.get("type")
    frequency_ = data.get("frequency")
    target_value = data.get("target_value")
    user_id = data.get("user_id")

    if not all([name, type_, target_value, user_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        habit_type = HabitType(type_)
        frequency = HabitFrequency(frequency_)
    except ValueError:
        return jsonify({"error": "Invalid type or frequency value"}), 400

    
    new_habit = Habit(
        name=name,
        type=habit_type,
        frequency=frequency,
        target_value=target_value,
        user_id=user_id
    )

    db.session.add(new_habit)
    db.session.commit()

    return jsonify({
        "id": new_habit.id,
        "name": new_habit.name,
        "type": new_habit.type.value,
        "frequency": new_habit.frequency.value,
        "target_value": new_habit.target_value,
        "user_id": new_habit.user_id,
    }), 201


@habits_bp.route("", methods=["GET"])
def fetch_habits():
    user_id = request.args.get("user_id", type=int)  # request.args for GET params!

    query = Habit.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    habits = query.all()

    return jsonify([
        {
            "id": habit.id,
            "name": habit.name,
            "type": habit.type.value,
            "target_value": habit.target_value,
            "frequency": habit.frequency.value,
            "user_id": habit.user_id,
        }
        for habit in habits
    ]), 200
