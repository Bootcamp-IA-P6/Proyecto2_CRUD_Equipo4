from pydantic import BaseModel, ConfigDict
from datetime import datetime
from domain.assignment_enum import AssignmentStatus
from typing import Optional


class AssignmentBase(BaseModel):
    project_skill_id: int
    volunteer_skill_id: int
    status: AssignmentStatus = AssignmentStatus.pending

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(AssignmentBase):
    project_skill_id: Optional[int] = None
    volunteer_skill_id: Optional[int] = None
    status: Optional[AssignmentStatus] = None
    
    model_config = ConfigDict(from_attributes=True)

class AssignmentOut(AssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


