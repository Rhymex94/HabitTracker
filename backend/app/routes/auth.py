from flask import Blueprint, request, jsonify
from app.models import db, User
from app.auth import (
    get_hashed_password,
    check_password,
    create_access_token,
    token_required,
)
from app.limiter import limiter
from app.validators import validate_auth_credentials

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("3 per hour")
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Validate credentials
    is_valid, error_message = validate_auth_credentials(username, password)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Username already exists"}), 400

    hashed_password = get_hashed_password(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    token = create_access_token(new_user.id)

    return (
        jsonify({
            "success": True,
            "data": {"token": token, "user_id": new_user.id, "username": new_user.username},
        }),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Check for required fields
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password(password, user.password):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    token = create_access_token(user.id)

    return jsonify({
        "success": True,
        "data": {"token": token, "user_id": user.id, "username": user.username},
    }), 200


@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token():
    return jsonify({"success": True, "message": "Token is valid"}), 200
