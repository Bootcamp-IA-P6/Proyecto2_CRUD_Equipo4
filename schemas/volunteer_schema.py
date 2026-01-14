from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class VolunteerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class VolunteerBase(BaseModel):
    user_id: int
    status: VolunteerStatus = VolunteerStatus.active


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    status: VolunteerStatus


class VolunteerOut(VolunteerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
