from app.controllers.project_controller import ProjectController
from app.schemas import project_schema
from datetime import datetime, timezone, timedelta
from app.tests.factories.project_factory import ProjectFactory
from app.tests.factories.category_factory import CategoryFactory
from app.domain.projects_enums import Project_status, Project_priority  
from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from fastapi import HTTPException
from app.tests.factories.skill_factory import SkillFactory
import pytest


@pytest.fixture(autouse=True)
def setup_pagination():
    """Configura parámetros de paginación para cada test"""
    set_params(Params(page=1, size=50))
    yield


# CREATE TESTS 
@pytest.mark.asyncio
async def test_create_project_success(db_session):
    """Test para crear un proyecto exitosamente"""

    category = CategoryFactory.create()
    
    project_data = project_schema.ProjectCreate(
        name="Nuevo Proyecto",
        description="Descripción del proyecto",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        status=Project_status.not_assigned,  
        priority=Project_priority.medium,    
        category_id=category.id
    )
    
  
    result = await ProjectController.create_project(db_session, project_data)
    
    assert result.id is not None
    assert result.name == "Nuevo Proyecto"
    assert result.description == "Descripción del proyecto"


@pytest.mark.asyncio
async def test_create_project_duplicate_name(db_session):
    """Test crear proyecto con nombre duplicado"""

    category = CategoryFactory.create()
    existing_project = ProjectFactory.create(name="Proyecto Único")
    
    project_data = project_schema.ProjectCreate(
        name="Proyecto Único",  # Mismo nombre
        description="Otra descripción",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        status=Project_status.not_assigned,  #
        priority=Project_priority.medium,   
        category_id=category.id
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.create_project(db_session, project_data)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Project already exist"
@pytest.mark.asyncio
async def test_get_projects_success(db_session):
    """Test para obtener lista de proyectos paginada"""
    
    category = CategoryFactory.create()
    ProjectFactory.create_batch(5)
    
    
    result = await ProjectController.get_projects(db_session)
    
    assert len(result.items) == 5
    assert result.total == 5


@pytest.mark.asyncio
async def test_get_projects_empty(db_session):
    """Test cuando no hay proyectos"""
    
    category = CategoryFactory.create()
    

    result = await ProjectController.get_projects(db_session)
    
    assert len(result.items) == 0
    assert result.total == 0


@pytest.mark.asyncio
async def test_get_projects_excludes_deleted(db_session):
    """Test que proyectos eliminados no aparecen en la lista"""
    
    category = CategoryFactory.create()
    active_project = ProjectFactory.create()
    deleted_project = ProjectFactory.create(deleted_at=datetime.now(timezone.utc))
    result = await ProjectController.get_projects(db_session)
    
    assert len(result.items) == 1
    assert result.items[0].id == active_project.id


@pytest.mark.asyncio
async def test_get_project_success(db_session):
    """Test para obtener un proyecto por ID"""
   
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    
    result = await ProjectController.get_project(db_session, project.id)
    

    assert result.id == project.id
    assert result.name == project.name
    assert result.description == project.description


@pytest.mark.asyncio
async def test_get_project_not_found(db_session):
    """Test cuando el proyecto no existe"""

    category = CategoryFactory.create()
    
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.get_project(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


@pytest.mark.asyncio
async def test_get_project_deleted(db_session):
    """Test que proyecto eliminado no se puede obtener"""
    category = CategoryFactory.create()
    deleted_project = ProjectFactory.create(deleted_at=datetime.now(timezone.utc))
    
    
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.get_project(db_session, deleted_project.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"
    
@pytest.mark.asyncio
async def test_update_project_success(db_session):
    """Test para actualizar un proyecto exitosamente"""

    category = CategoryFactory.create()
    project = ProjectFactory.create()
    
    update_data = project_schema.ProjectUpdate(
        name="Proyecto Actualizado",
        description="Nueva descripción",
        status=Project_status.assigned,
        priority=Project_priority.high
    )
    
    result = await ProjectController.update_project(db_session, project.id, update_data)
    

    assert result.id == project.id
    assert result.name == "Proyecto Actualizado"
    assert result.description == "Nueva descripción"
    assert result.status == Project_status.assigned
    assert result.priority == Project_priority.high


@pytest.mark.asyncio
async def test_update_project_not_found(db_session):
    """Test actualizar proyecto que no existe"""
    
    category = CategoryFactory.create()
    
    update_data = project_schema.ProjectUpdate(name="Test")
    
   
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.update_project(db_session, 999, update_data)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project no found"


@pytest.mark.asyncio
async def test_update_project_partial(db_session):
    """Test actualización parcial (solo algunos campos)"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create(
        name="Original",
        description="Descripción Original",
        priority=Project_priority.low
    )
    
    update_data = project_schema.ProjectUpdate(name="Nuevo Nombre")
    
  
    result = await ProjectController.update_project(db_session, project.id, update_data)
    
    assert result.name == "Nuevo Nombre"
    assert result.description == "Descripción Original"  # No cambió
    assert result.priority == Project_priority.low  # No cambió


@pytest.mark.asyncio
async def test_update_project_deadline(db_session):
    """Test actualizar deadline de proyecto"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    
    new_deadline = datetime.now(timezone.utc) + timedelta(days=60)
    update_data = project_schema.ProjectUpdate(deadline=new_deadline)
    
  
    result = await ProjectController.update_project(db_session, project.id, update_data)
    
    assert result.deadline.date() == new_deadline.date()



@pytest.mark.asyncio
async def test_delete_project_not_found(db_session):
    """Test eliminar proyecto que no existe"""
    
    category = CategoryFactory.create()
    
   
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.delete_project(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


@pytest.mark.asyncio
async def test_delete_project_already_deleted(db_session):
    """Test eliminar proyecto que ya fue eliminado"""
    
    category = CategoryFactory.create()
    deleted_project = ProjectFactory.create(deleted_at=datetime.now(timezone.utc))
    
   
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.delete_project(db_session, deleted_project.id)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Project already deleted"
    
@pytest.mark.asyncio
async def test_add_skill_to_project_success(db_session):
    """Test para agregar una skill a un proyecto"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    skill = SkillFactory.create()
    
  
    result = await ProjectController.add_skill_to_project(db_session, project.id, skill.id)
    
    assert result.id == project.id
    assert len(result.skills) > 0


@pytest.mark.asyncio
async def test_add_skill_to_project_not_found(db_session):
    """Test agregar skill a proyecto que no existe"""
    
    category = CategoryFactory.create()
    skill = SkillFactory.create()
    
   
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.add_skill_to_project(db_session, 999, skill.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


@pytest.mark.asyncio
async def test_add_skill_duplicate(db_session):
    """Test agregar skill que ya existe en el proyecto"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    skill = SkillFactory.create()
    
    # Agregar skill por primera vez
    await ProjectController.add_skill_to_project(db_session, project.id, skill.id)
    
    #Intentar agregar la misma skill
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.add_skill_to_project(db_session, project.id, skill.id)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "project already has this skill"


@pytest.mark.asyncio
async def test_get_project_with_skills_success(db_session):
    """Test obtener proyecto con sus skills"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    skill1 = SkillFactory.create()
    skill2 = SkillFactory.create()
    
    await ProjectController.add_skill_to_project(db_session, project.id, skill1.id)
    await ProjectController.add_skill_to_project(db_session, project.id, skill2.id)
    
  
    result = await ProjectController.get_project_with_skills(db_session, project.id)
    
    assert result.id == project.id
    assert len(result.skills) == 2


@pytest.mark.asyncio
async def test_get_project_with_skills_not_found(db_session):
    """Test obtener skills de proyecto que no existe"""
    
    category = CategoryFactory.create()
    
   
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.get_project_with_skills(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"



@pytest.mark.asyncio
async def test_remove_skill_not_assigned(db_session):
    """Test remover skill que no está asignada al proyecto"""
    
    category = CategoryFactory.create()
    project = ProjectFactory.create()
    skill = SkillFactory.create()
    
    #Intentar remover sin haberla agregado
    with pytest.raises(HTTPException) as exc_info:
        await ProjectController.remove_skill_from_project(db_session, project.id, skill.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Skill not assigned to project"





