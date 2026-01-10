import os
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging
import sys
from flask_cors import CORS

from . import models
from app.limiter import limiter
from app.routes.habits import habits_bp
from app.routes.progress import progress_bp
from app.routes.stats import stats_bp
from app.routes.auth import auth_bp


db = models.db
migrate = Migrate()

def create_app(configs = None):
    app = Flask(__name__)

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    CORS(
        app,
        origins=[frontend_origin],
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
