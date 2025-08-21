import pytest
from datetime import date, timedelta

from app.enums import HabitFrequency, HabitType
from app.models import Habit, ProgressEntry
from app.routes.stats import calculate_streak, get_date_range
from tests.mocks import MockHabit, MockProgressEntry


@pytest.mark.parametrize(
    "current_date, frequency, expected_start, expected_end",
    [
        # DAILY
        (date(2025, 8, 10), HabitFrequency.DAILY, date(2025, 8, 10), date(2025, 8, 11)),
        # WEEKLY: 2025-08-10 is Sunday, so start = Monday 4th, end = Monday 11th
        (date(2025, 8, 10), HabitFrequency.WEEKLY, date(2025, 8, 4), date(2025, 8, 11)),
        # MONTHLY normal month: August 2025, start 1st, end 1st Sept
        (date(2025, 8, 10), HabitFrequency.MONTHLY, date(2025, 8, 1), date(2025, 9, 1)),
        # MONTHLY December: boundary case year rollover
        (date(2025, 12, 15), HabitFrequency.MONTHLY, date(2025, 12, 1), date(2026, 1, 1)),
        # YEARLY normal year
        (date(2025, 8, 10), HabitFrequency.YEARLY, date(2025, 1, 1), date(2026, 1, 1)),
        # YEARLY leap year boundary test
        (date(2024, 2, 29), HabitFrequency.YEARLY, date(2024, 1, 1), date(2025, 1, 1)),
    ],
)
def test_get_date_range(current_date, frequency, expected_start, expected_end):
    start, end = get_date_range(current_date, frequency)
    assert start == expected_start
    assert end == expected_end


def _make_entries(dates_and_values):
    sorted_items = sorted(dates_and_values, key=lambda x: x[0], reverse=True)
    return [MockProgressEntry(d, v) for d, v in sorted_items]


def test_calculate_streak_daily_above():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.ABOVE, target_value=10)
    today = date.today()

    # Entries exactly meeting target yesterday and day before, but not today yet
    entries = _make_entries(
        [
            (today - timedelta(days=1), 10),
            (today - timedelta(days=2), 10),
            (today - timedelta(days=3), 5),  # less than target breaks streak
        ]
    )

    streak = calculate_streak(habit, entries)
    assert streak == 2  # 2 days streak, stopped by day -3


def test_calculate_streak_daily_above_with_today_entry():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.ABOVE, target_value=10)
    today = date.today()

    entries = _make_entries(
        [
            (today, 5),  # today partial progress
            (today - timedelta(days=1), 10),
            (today - timedelta(days=2), 10),
        ]
    )

    streak = calculate_streak(habit, entries)
    # Since today hasn't reached target, but streak counts only complete previous days
    assert streak == 2


def test_calculate_streak_daily_below():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.BELOW, target_value=1)
    today = date.today()

    entries = _make_entries(
        [
            (today - timedelta(days=1), 1),
            (today - timedelta(days=2), 1),
            (today - timedelta(days=3), 0),  # missed day breaks streak
        ]
    )

    streak = calculate_streak(habit, entries)
    assert streak == 2


def test_calculate_streak_weekly():
    habit = MockHabit(HabitFrequency.WEEKLY, HabitType.ABOVE, target_value=5)
    today = date.today()
    # Let's assume weeks start on Monday, create entries for last two weeks hitting targets
    current_week_start, _ = get_date_range(today, HabitFrequency.WEEKLY)
    last_week_start = current_week_start - timedelta(days=7)

    entries = _make_entries(
        [
            (current_week_start + timedelta(days=3), 3),  # partial week, less than target
            (last_week_start + timedelta(days=2), 5),  # full target last week
            (
                last_week_start - timedelta(days=1),
                4,
            ),  # older week, below target breaks streak
        ]
    )

    streak = calculate_streak(habit, entries)
    # Current week is incomplete/partial, so only count last week full target = 1 streak
    assert streak == 1


def test_calculate_streak_break_in_streak():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.ABOVE, target_value=5)
    today = date.today()

    entries = _make_entries(
        [
            (today - timedelta(days=1), 5),
            (today - timedelta(days=2), 2),  # below target breaks streak
            (today - timedelta(days=3), 5),
        ]
    )

    streak = calculate_streak(habit, entries)
    assert streak == 1  # streak stops after day-2


def test_calculate_streak_empty_progress():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.ABOVE, target_value=5)
    entries = []

    streak = calculate_streak(habit, entries)
    assert streak == 0


def test_binary_habit_done_then_undone():
    habit = MockHabit(HabitFrequency.DAILY, HabitType.ABOVE, target_value=1)
    today = date.today()

    entries = _make_entries(
        [
            (today - timedelta(days=1), 1),
            (today - timedelta(minutes=10), 1),
            (today - timedelta(minutes=5), -1),
        ]
    )

    streak = calculate_streak(habit, entries)
    assert streak == 1


@pytest.mark.parametrize(
    "mock_habits, mock_progress_entries",
    [
        (
            {
                "habits": [
                    {
                        "id": 1,
                        "name": "Drink water",
                        "frequency": HabitFrequency.DAILY,
                        "type": HabitType.ABOVE,
                        "target_value": 8,
                    },
                    {
                        "id": 2,
                        "name": "Go for a run",
                        "frequency": HabitFrequency.WEEKLY,
                        "type": HabitType.ABOVE,
                        "target_value": 1,
                    },
                ],
                "path": "app.routes.stats.Habit.query",
            },
            {
                "entries": [
                    ProgressEntry(habit_id=1, date=date(2025, 8, 9), value=8),
                    ProgressEntry(habit_id=2, date=date(2025, 8, 8), value=1),
                ],
                "path": "app.routes.stats.db.session.query",
            },
        )
    ],
    indirect=True,
)
def test_get_stats(client, mock_habits, mock_progress_entries, monkeypatch, test_auth_headers):
    # Mock calculate_streak to return a predictable value
    monkeypatch.setattr("app.routes.stats.calculate_streak", lambda habit, entries: 99)

    res = client.get("/api/stats", headers=test_auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data == {"1": 99, "2": 99}
