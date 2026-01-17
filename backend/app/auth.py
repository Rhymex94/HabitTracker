from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
import bcrypt
from flask import current_app, request, jsonify
from app.security_logger import log_token_validation_failure, log_unauthorized_access


def get_hashed_password(plain_text_password: str) -> bytes:
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())


def check_password(plain_text_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)


def create_access_token(user_id: int) -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
        "sub": user_id,
    }
    secret_key = str(current_app.config.get("SECRET_KEY", ""))
    if not secret_key:
        raise ValueError("SECRET_KEY not configured")

    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        secret_key = str(current_app.config.get("SECRET_KEY", ""))
        if not secret_key:
            raise ValueError("SECRET_KEY not configured")

        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                log_token_validation_failure("invalid_format")
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            log_unauthorized_access(request.path, request.method, "missing_token")
            return jsonify({"error": "Token is missing"}), 401

        try:
            payload = decode_token(token)
            request.user_id = payload["sub"]
        except ValueError as e:
            log_token_validation_failure(str(e))
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated
