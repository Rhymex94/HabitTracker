import os
import sys


def get_secret_key():
    """Get SECRET_KEY from environment or fail if not in development mode."""
    secret_key = os.getenv("SECRET_KEY")

    if secret_key:
        return secret_key

    # Check if explicitly set to development
    is_development = (
        os.getenv("FLASK_ENV") == "development"
        or os.getenv("ENVIRONMENT") == "development"
    )

    if is_development:
        # In development mode, use the default key
        print("WARNING: Using default SECRET_KEY for development. Do not use in production!", file=sys.stderr)
        return "dev-secret-key-123"

    # By default, assume production and require SECRET_KEY
    print("ERROR: SECRET_KEY environment variable is required", file=sys.stderr)
    print("For development, set FLASK_ENV=development or ENVIRONMENT=development", file=sys.stderr)
    print("For production, generate a secure key with: python -c 'import secrets; print(secrets.token_hex(32))'", file=sys.stderr)
    sys.exit(1)


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/habits_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = get_secret_key()
    DEBUG = True