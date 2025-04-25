from flask import Flask
from flask_migrate import Migrate

from . import models
from app.routes.habits import habits_bp


db = models.db
migrate = Migrate()

def create_app(configs = None):
    app = Flask(__name__)

    if configs:
        app.config.from_object(configs)
    else:
        app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(habits_bp)

    return app