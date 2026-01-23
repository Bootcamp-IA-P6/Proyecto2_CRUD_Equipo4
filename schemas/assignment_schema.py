from pydantic import BaseModel, ConfigDict
from datetime import datetime
from domain.assignment_enum import AssignmentStatus
from typing import Optional


# ============================================
# Schemas básicos para datos relacionados
# ============================================

class SkillBasicInfo(BaseModel):
    """Información básica de una skill"""
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class VolunteerBasicInfo(BaseModel):
    """Información básica de un voluntario para assignments"""
    id: int
    user_id: int
    user_name: str | None = None
    # se pueden agregar más campos si tiene relación con User
    # Por ejemplo: name, email desde la tabla users
    
    model_config = ConfigDict(from_attributes=True)


class ProjectBasicInfo(BaseModel):
    """Información básica de un proyecto para assignments"""
    id: int
    name: str
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schemas base de Assignment
# ============================================

class AssignmentBase(BaseModel):
    project_skill_id: int
    volunteer_skill_id: int
    status: AssignmentStatus = AssignmentStatus.PENDING


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    project_skill_id: Optional[int] = None
    volunteer_skill_id: Optional[int] = None
    status: Optional[AssignmentStatus] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schema de salida BÁSICO 
# ============================================

class AssignmentOut(AssignmentBase):
    """Schema básico de salida - mantiene compatibilidad"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schema ENRIQUECIDO para POST (crear assignment)
# ============================================

class AssignmentCreateResponse(AssignmentOut):
    """
    Respuesta enriquecida al crear un assignment.
    Incluye: volunteer, project y la skill que hizo match
    """
    volunteer: VolunteerBasicInfo
    project: ProjectBasicInfo
    matched_skill: SkillBasicInfo
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schema para GET by Project
# ============================================

class AssignmentByProject(BaseModel):
    """
    Assignment visto desde un proyecto.
    Muestra: voluntarios asignados y sus skills
    """
    id: int
    status: AssignmentStatus
    created_at: datetime
    volunteer: VolunteerBasicInfo
    matched_skill: SkillBasicInfo
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schema para GET by Volunteer  
# ============================================

class AssignmentByVolunteer(BaseModel):
    """
    Assignment visto desde un voluntario.
    Muestra: proyectos asignados y skills usadas
    """
    id: int
    status: AssignmentStatus
    created_at: datetime
    project: ProjectBasicInfo
    matched_skill: SkillBasicInfo
    
    model_config = ConfigDict(from_attributes=True)