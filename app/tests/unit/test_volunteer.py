from app.controllers.volunteer_controller import (
    create_volunteer,
    get_volunteers,
    get_volunteer,
    update_volunteer,
    delete_volunteer,
    get_volunteer_with_skills,
    add_skill_to_volunteer,
    remove_skill_from_volunteer
)
from app.schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from datetime import datetime, timezone
from app.tests.factories.volunteer_factory import VolunteerFactory
from app.tests.factories.user_factory import UserFactory
from app.tests.factories.role_factory import RoleFactory
from app.tests.factories.skill_factory import SkillFactory
from app.domain.volunteer_enum import VolunteerStatus
from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from fastapi import HTTPException
import pytest


@pytest.fixture(autouse=True)
def setup_pagination():
    """Configura parámetros de paginación para cada test"""
    set_params(Params(page=1, size=50))
    yield


def test_create_volunteer_success(db_session):
    """Test para crear un voluntario exitosamente"""
   
    role = RoleFactory.default()
    user = UserFactory.create()
    
    volunteer_data = VolunteerCreate(
        user_id=user.id,
        status=VolunteerStatus.active
    )
    
    result = create_volunteer(db_session, volunteer_data)
    
    assert result.id is not None
    assert result.user_id == user.id
    assert str(result.status).split('.')[-1] == "active" 


def test_create_volunteer_user_not_found(db_session):
    """Test crear voluntario con usuario inexistente"""
   
    role = RoleFactory.default()
    
    volunteer_data = VolunteerCreate(
        user_id=999,
        status=VolunteerStatus.active
    )
    
   
    with pytest.raises(HTTPException) as exc_info:
        create_volunteer(db_session, volunteer_data)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_get_volunteers_success(db_session):
    """Test para obtener lista de voluntarios"""
    role = RoleFactory.default()
    VolunteerFactory.create_batch(3)
    
    result = get_volunteers(db_session)
    
    assert len(result.items) == 3
    assert result.total == 3


def test_get_volunteers_empty(db_session):
    """Test cuando no hay voluntarios"""
   
    role = RoleFactory.default()
    
    result = get_volunteers(db_session)
    
    assert len(result.items) == 0
    assert result.total == 0


def test_get_volunteers_excludes_deleted(db_session):
    """Test que voluntarios eliminados no aparecen"""
   
    role = RoleFactory.default()
    active = VolunteerFactory.create()
    deleted = VolunteerFactory.create(deleted_at=datetime.now(timezone.utc))
    
    result = get_volunteers(db_session)
    
    assert len(result.items) == 1
    assert result.items[0].id == active.id


# def test_get_volunteer_success(db_session):
#     """Test obtener voluntario por ID"""
   
#     role = RoleFactory.default()
#     volunteer = VolunteerFactory.create()
    
#     result = get_volunteer(db_session, volunteer.id)
    
#     assert result.id == volunteer.id
#     assert result.user_id == volunteer.user_id


def test_get_volunteer_not_found(db_session):
    """Test voluntario no encontrado"""
   
    role = RoleFactory.default()
    
   
    with pytest.raises(HTTPException) as exc_info:
        get_volunteer(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Volunteer not found"



# def test_update_volunteer_success(db_session):
#     """Test actualizar status de voluntario"""
   
#     role = RoleFactory.default()
#     volunteer = VolunteerFactory.create(status=VolunteerStatus.active)
    
#     update_data = VolunteerUpdate(status=VolunteerStatus.inactive)
    
#     result = update_volunteer(db_session, volunteer.id, update_data)
    
#     assert result.id == volunteer.id
#     assert result.status == VolunteerStatus.inactive 


def test_update_volunteer_not_found(db_session):
    """Test actualizar voluntario inexistente"""
   
    role = RoleFactory.default()
    update_data = VolunteerUpdate(status=VolunteerStatus.inactive)
    
   
    with pytest.raises(HTTPException) as exc_info:
        update_volunteer(db_session, 999, update_data)
    
    assert exc_info.value.status_code == 404
    


def test_delete_volunteer_not_found(db_session):
    """Test eliminar voluntario inexistente"""
   
    role = RoleFactory.default()
    
  
    with pytest.raises(HTTPException) as exc_info:
        delete_volunteer(db_session, 999)
    
    assert exc_info.value.status_code == 404


def test_delete_volunteer_already_deleted(db_session):
    """Test eliminar voluntario ya eliminado"""
   
    role = RoleFactory.default()
    deleted = VolunteerFactory.create(deleted_at=datetime.now(timezone.utc))
    
  
    with pytest.raises(HTTPException) as exc_info:
        delete_volunteer(db_session, deleted.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Volunteer not found"



# def test_get_volunteer_with_skills_success(db_session):
#     """Test obtener voluntario con sus skills"""

#     role = RoleFactory.default()
#     volunteer = VolunteerFactory.create()
#     skill1 = SkillFactory.create()
#     skill2 = SkillFactory.create()
    
#     add_skill_to_volunteer(db_session, volunteer.id, skill1.id)
#     add_skill_to_volunteer(db_session, volunteer.id, skill2.id)
    
  
#     result = get_volunteer_with_skills(db_session, volunteer.id)
    
  
#     assert result.id == volunteer.id
#     assert len(result.skills) == 2


# def test_add_skill_to_volunteer_success(db_session):
#     """Test agregar skill a voluntario"""
   
#     role = RoleFactory.default()
#     volunteer = VolunteerFactory.create()
#     skill = SkillFactory.create()
    
  
#     result = add_skill_to_volunteer(db_session, volunteer.id, skill.id)
    
  
#     assert result.id == volunteer.id


def test_add_skill_volunteer_not_found(db_session):
    """Test agregar skill a voluntario inexistente"""
   
    role = RoleFactory.default()
    skill = SkillFactory.create()
    
  
    with pytest.raises(HTTPException) as exc_info:
        add_skill_to_volunteer(db_session, 999, skill.id)
    
    assert exc_info.value.status_code == 404


# def test_add_skill_duplicate(db_session):
#     """Test agregar skill duplicada"""
   
#     role = RoleFactory.default()
#     volunteer = VolunteerFactory.create()
#     skill = SkillFactory.create()
    
#     add_skill_to_volunteer(db_session, volunteer.id, skill.id)
    
  
#     with pytest.raises(HTTPException) as exc_info:
#         add_skill_to_volunteer(db_session, volunteer.id, skill.id)
    
#     assert exc_info.value.status_code == 409