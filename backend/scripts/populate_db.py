import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from app import create_app, db
from app.enums import HabitType, HabitFrequency
from app.models import User, Habit, ProgressEntry
import random
import datetime

app = create_app()

# We want to use this inside the app context
with app.app_context():
    # Clear existing data (optional, if you want a fresh start each time)
    db.drop_all()
    db.create_all()

    # Create a test user
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    # Add some test habits
    habits = [
        Habit(
            name="Exercise",
            type=HabitType.ABOVE,
            frequency=HabitFrequency.DAILY,
            target_value=30,
            user_id=user.id,
        ),
        Habit(
            name="Read",
            type=HabitType.ABOVE,
            frequency=HabitFrequency.DAILY,
            target_value=20,
            user_id=user.id,
        ),
        Habit(
            name="Meditate",
            type=HabitType.ABOVE,
            frequency=HabitFrequency.DAILY,
            target_value=1,
            user_id=user.id,
        ),
    ]

    db.session.add_all(habits)
    db.session.commit()

    # Add some progress entries for each habit
    for habit in habits:
        for i in range(1, 11):  # 10 days of progress
            date = datetime.date.today() - datetime.timedelta(days=i)
            value = random.randint(10, 45)

            progress_entry = ProgressEntry(date=date, value=value, habit_id=habit.id)
            db.session.add(progress_entry)

    db.session.commit()

    print("Test data populated!")
