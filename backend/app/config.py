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
    DEBUG = os.getenv("ENVIRONMENT") != "production"

    # Connection pooling configuration for production performance
    # These settings help manage database connections efficiently under load
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),  # Number of persistent connections
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),  # Extra connections when pool is exhausted
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),  # Seconds to wait for available connection
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),  # Recycle connections after 30 min (avoid MySQL timeout)
        "pool_pre_ping": True,  # Verify connection is alive before using (prevents stale connection errors)
    }