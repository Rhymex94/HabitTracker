from datetime import date
from flask_sqlalchemy import SQLAlchemy

from app.enums import HabitFrequency, HabitType

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    habits = db.relationship("Habit", backref="user", lazy=True)


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    type = db.Column(db.Enum(HabitType), nullable=False)

    # Target definition
    frequency = db.Column(db.Enum(HabitFrequency), nullable=False)
    target_value = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # Use the below to get access directly to the user.
    # user = db.relationship("User", backref="habits")

    progress_entries = db.relationship(
        "ProgressEntry",
        backref="habit",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    start_date = db.Column(db.Date, nullable=False, default=date.today)


class ProgressEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    habit_id = db.Column(
        db.Integer,
        db.ForeignKey("habit.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Composite index for the common query pattern: filter by habit_id and date range
    __table_args__ = (
        db.Index("ix_progress_entry_habit_date", "habit_id", "date"),
    )
