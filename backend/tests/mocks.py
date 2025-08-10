

class MockHabit:
    def __init__(self, frequency, type_, target_value):
        self.frequency = frequency
        self.type = type_
        self.target_value = target_value


class MockProgressEntry:
    def __init__(self, date, value):
        self.date = date
        self.value = value