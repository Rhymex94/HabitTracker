import enum

class HabitType(enum.Enum):
    BINARY = 0
    QUANTITATIVE = 1


class HabitFrequency(enum.Enum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    YEARLY = 3

