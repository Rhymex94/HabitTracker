import os
import sys
from urllib.parse import urlparse
from flask import Flask
from flask_migrate import Migrate
from flask_talisman import Talisman
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_cors import CORS

from . import models
from app.limiter import limiter
from app.routes.habits import habits_bp
from app.routes.progress import progress_bp
from app.routes.stats import stats_bp
from app.routes.auth import auth_bp


db = models.db
migrate = Migrate()


def validate_cors_origin(origin: str) -> bool:
    """Validate that a CORS origin is a properly formatted URL."""
    if not origin:
        return False
    try:
        parsed = urlparse(origin)
        # Must have http or https scheme and a netloc (domain)
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc:
            return False
        # Should not have path (other than /), query, or fragment
        if parsed.path and parsed.path != "/":
            return False
        return True
    except Exception:
        return False


def get_cors_origins() -> list[str]:
    """Get and validate CORS origins from environment variable.

    Supports multiple origins separated by commas for staging/production.
    Example: FRONTEND_ORIGIN=https://app.example.com,https://staging.example.com
    """
    raw_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    if not origins:
        print("ERROR: FRONTEND_ORIGIN environment variable is empty", file=sys.stderr)
        sys.exit(1)

    invalid_origins = [o for o in origins if not validate_cors_origin(o)]
    if invalid_origins:
        print("ERROR: Invalid FRONTEND_ORIGIN value(s):", file=sys.stderr)
        for origin in invalid_origins:
            print(f"  - '{origin}'", file=sys.stderr)
        print("", file=sys.stderr)
        print("FRONTEND_ORIGIN must be a valid URL with http:// or https:// protocol.", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  FRONTEND_ORIGIN=http://localhost:3000", file=sys.stderr)
        print("  FRONTEND_ORIGIN=https://myapp.example.com", file=sys.stderr)
        print("  FRONTEND_ORIGIN=https://app.example.com,https://staging.example.com", file=sys.stderr)
        sys.exit(1)

    return origins

def create_app(configs = None):
    app = Flask(__name__)

    # Enforce HTTPS in production (must be before other middleware)
    if os.environ.get("ENVIRONMENT") == "production":
        Talisman(app, force_https=True, content_security_policy=None)

    cors_origins = get_cors_origins()
    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
    )

    if configs:
        app.config.from_object(configs)
    else:
        app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")
    app.register_blueprint(progress_bp, url_prefix="/api/progress")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")

    return app


# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    from sqlite3 import Connection as SQLite3Connection

    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
