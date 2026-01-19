from enum import Enum

class VolunteerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
