class MockHabit:

    def __init__(self, frequency, type_, target_value, start_date):
        self.frequency = frequency
        self.type = type_
        self.target_value = target_value
        self.start_date = start_date


class MockProgressEntry:
    def __init__(self, date, value):
        self.date = date
        self.value = value
