class MockHabit:

    def __init__(self, frequency, type_, target_value, start_date, id=None):
        self.id = id
        self.frequency = frequency
        self.type = type_
        self.target_value = target_value
        self.start_date = start_date


class MockProgressEntry:
    def __init__(self, date, value, habit_id=None):
        self.date = date
        self.value = value
        self.habit_id = habit_id
