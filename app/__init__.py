from flask import Flask
from flask_migrate import Migrate

from . import models
from .routes import main



# db = SQLAlchemy()
db = models.db
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)

    return app