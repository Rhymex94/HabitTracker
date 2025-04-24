from flask import Blueprint, jsonify

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return jsonify(message="Habit Tracker API is running!")
