from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus

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


    model_config = ConfigDict(from_attributes=True)

