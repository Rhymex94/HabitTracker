from flask import Blueprint, request, jsonify
from app.models import db, User
from app.auth import (
    get_hashed_password,
    check_password,
    create_access_token,
    token_required,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = get_hashed_password(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    token = create_access_token(new_user.id)

    return (
        jsonify({"token": token, "user_id": new_user.id, "username": new_user.username}),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password(password, user.password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(user.id)

    return jsonify({"token": token, "user_id": user.id, "username": user.username}), 200


@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token():
    return jsonify({"message": "Token is valid"}), 200
