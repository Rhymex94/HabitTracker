import enum

class HabitType(enum.Enum):
    BINARY = 1
    QUANTITATIVE = 2


class HabitFrequency(enum.Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4

