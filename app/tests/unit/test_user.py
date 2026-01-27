from app.controllers.users_controller import UserController
from app.schemas.users_schema import UserCreate
from app.schemas import users_schema
from datetime import date, datetime, timezone
from app.tests.factories.role_factory import RoleFactory
from app.tests.factories.user_factory import UserFactory
from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from fastapi import HTTPException  
import pytest


@pytest.fixture(autouse=True)
def setup_pagination():
    """Configura parámetros de paginación para cada test"""
    set_params(Params(page=1, size=50))
    yield


def test_create_user_success(db_session):
    role = RoleFactory.default()
    
    user_data = UserCreate(
        name="Ingrid Dev",
        email="ingrid@test.com",
        password="123456",
        phone="600111222",
        birth_date=date(1998, 5, 10)
    )

    created_user = UserController.create_user(db_session, user_data)

    assert created_user.id is not None
    assert created_user.email == "ingrid@test.com"
    assert created_user.name == "Ingrid Dev"
    assert created_user.password != "123456"


def test_get_users_success(db_session):
    """Test para obtener lista de usuarios paginada"""
    role = RoleFactory.default()
    UserFactory.create_batch(5)
    
    result = UserController.get_users(db_session)
    
    assert len(result.items) == 5
    assert result.total == 5


def test_get_users_empty(db_session):
    """Test cuando no hay usuarios"""
    role = RoleFactory.default()
    
    result = UserController.get_users(db_session)
    
    assert len(result.items) == 0
    assert result.total == 0


def test_get_users_excludes_deleted(db_session):
    """Test que usuarios eliminados no aparecen en la lista"""
    role = RoleFactory.default()
    
    active_user = UserFactory.create()
    deleted_user = UserFactory.create(deleted_at=datetime.now(timezone.utc))
    
    result = UserController.get_users(db_session)
    
    assert len(result.items) == 1
    assert result.items[0].id == active_user.id



def test_get_one_user_success(db_session):
    """Test para obtener un usuario por ID"""
    
    role = RoleFactory.default()
    user = UserFactory.create()
    
    
    result = UserController.get_one_user(db_session, user.id)
    
    
    assert result.id == user.id
    assert result.email == user.email
    assert result.name == user.name


def test_get_one_user_not_found(db_session):
    """Test cuando el usuario no existe"""
    
    role = RoleFactory.default()
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.get_one_user(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_get_one_user_deleted(db_session):
    """Test que usuario eliminado no se puede obtener"""
    
    role = RoleFactory.default()
    deleted_user = UserFactory.create(deleted_at=datetime.now(timezone.utc))
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.get_one_user(db_session, deleted_user.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
def test_update_user_success(db_session):
    """Test para actualizar un usuario exitosamente"""
    
    role = RoleFactory.default()
    user = UserFactory.create()
    
    from app.schemas.users_schema import UserUpdate
    update_data = UserUpdate(
        name="Nombre Actualizado",
        email="nuevo@email.com",
        phone="666777888"
    )
    
    
    result = UserController.update_user(db_session, user.id, update_data)
    
    
    assert result.id == user.id
    assert result.name == "Nombre Actualizado"
    assert result.email == "nuevo@email.com"
    assert result.phone == "666777888"


def test_update_user_not_found(db_session):
    """Test actualizar usuario que no existe"""
    
    role = RoleFactory.default()
    
    from app.schemas.users_schema import UserUpdate
    update_data = UserUpdate(name="Test")
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.update_user(db_session, 999, update_data)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_update_user_duplicate_email(db_session):
    """Test actualizar con email que ya existe"""
    
    role = RoleFactory.default()
    user1 = UserFactory.create(email="user1@test.com")
    user2 = UserFactory.create(email="user2@test.com")
    
    from app.schemas.users_schema import UserUpdate
    update_data = UserUpdate(email="user1@test.com")  
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.update_user(db_session, user2.id, update_data)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already exists"


def test_update_user_partial(db_session):
    """Test actualización parcial (solo algunos campos)"""
    
    role = RoleFactory.default()
    user = UserFactory.create(name="Original", email="original@test.com")
    
    from app.schemas.users_schema import UserUpdate
    update_data = UserUpdate(name="Nuevo Nombre")  
    
    
    result = UserController.update_user(db_session, user.id, update_data)
    
    
    assert result.name == "Nuevo Nombre"
    assert result.email == "original@test.com"  
def test_delete_user_success(db_session):
    """Test para eliminar un usuario (soft delete)"""
    
    role = RoleFactory.default()
    user = UserFactory.create()
    
    
    result = UserController.delete_user(db_session, user.id)
    assert result == {"message": "User deleted successfully"}
    db_session.refresh(user)
    assert user.deleted_at is not None


def test_delete_user_not_found(db_session):
    """Test eliminar usuario que no existe"""
    
    role = RoleFactory.default()
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.delete_user(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_delete_user_already_deleted(db_session):
    """Test eliminar usuario que ya fue eliminado"""
    
    role = RoleFactory.default()
    deleted_user = UserFactory.create(deleted_at=datetime.now(timezone.utc))
    
    
    with pytest.raises(HTTPException) as exc_info:
        UserController.delete_user(db_session, deleted_user.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_delete_user_and_verify_not_in_list(db_session):
    """Test que usuario eliminado no aparece en la lista"""
    
    role = RoleFactory.default()
    user1 = UserFactory.create()
    user2 = UserFactory.create()
   
    UserController.delete_user(db_session, user1.id)
    
    
    result = UserController.get_users(db_session)
    assert len(result.items) == 1
    assert result.items[0].id == user2.id