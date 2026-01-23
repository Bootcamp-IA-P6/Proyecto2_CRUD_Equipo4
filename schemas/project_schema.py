from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from domain.projects_enums import Project_status, Project_priority
from schemas.category_schemas import CategoryOut
from schemas.skills_schema import SkillOut


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: datetime
    status: Project_status = Project_status.not_assigned
    priority: Project_priority = Project_priority.medium
    category_id : int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[Project_status] = None
    priority: Optional[Project_priority] = None
    category_id : Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    category: Optional[CategoryOut] = None
    
    model_config = ConfigDict(from_attributes=True)


# operaciones de añadir o eliminar multiples skills
class ProjectSkillsOperation(BaseModel):
    project_id: int
    skill_ids: List[int]

class ProjectSkillsOut(ProjectOut):
    
    skills: List[SkillOut]  # Lista objetos Skill
