from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from schemas.project_schema import ProjectOut
from schemas.skill_schema import SkillOut


class ProjectSkillBase(BaseModel):
    project_id: int
    skill_id: int


class ProjectSkillCreate(ProjectSkillBase):
    pass


class ProjectSkillOut(ProjectSkillBase):

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    project: Optional[ProjectOut] = None
    skill: Optional[SkillOut] = None
    
    model_config = ConfigDict(from_attributes=True)



# Para operaciones bulk (añadir/quitar múltiples skills)
class ProjectSkillsBulkOperation(BaseModel):
    project_id: int
    skill_ids: list[int]  


#lista completa de skills para un project_id
class ProjectSkillsListOut(BaseModel):
    project_id: int
    project_name: str
    skills: list[dict] 
    
    model_config = ConfigDict(from_attributes=True)

