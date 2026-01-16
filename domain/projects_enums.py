import enum


class Project_status(enum.Enum):
    not_assigned = "not assigned"
    assigned = "assigned"
    completed="completed"

class Project_priority(enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"