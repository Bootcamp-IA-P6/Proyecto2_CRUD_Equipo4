from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    pass

class SkillOut(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)