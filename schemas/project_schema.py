from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from models.project_model import Project_status, Project_priority


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: datetime
    status: Project_status = Field(default=Project_status.not_asigned, description="Project status")
    priority: Project_priority = Field(default=Project_priority.medium, description="Project priority")
    #category_id : int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    create_at :datetime
    update_at : datetime
    status : str
    priority : str



    class Config:
        orm_mode = True # permite que Pydantic lea directamente objetos de SQLAlchemy como si fueran diccionarios, para enviarlos en respuestas JSON.