import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from app import create_app, db

app = create_app()

# We want to use this inside the app context
with app.app_context():
    # Drop all tables and reset the database
    db.drop_all()
    db.create_all()

    print("Database reset complete!")