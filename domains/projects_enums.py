import enum


class Project_status(enum.Enum):
    not_asigned = "not asigned"
    asigned = "asigned"
    completed="completed"

class Project_priority(enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"