from pydantic import BaseModel, ConfigDict
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus
from typing import Optional

class VolunteerBase(BaseModel):
    user_id: int
    status: VolunteerStatus = VolunteerStatus.active


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    status: VolunteerStatus


class VolunteerOut(VolunteerBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at : Optional[datetime]


    model_config = ConfigDict(from_attributes=True)

