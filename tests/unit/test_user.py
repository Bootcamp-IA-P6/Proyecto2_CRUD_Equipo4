# tests/unit/test_user.py
from controllers.users_controller import UserController
from schemas.users_schema import UserCreate
from schemas import users_schema
from datetime import date, datetime, timezone
from tests.factories.role_factory import RoleFactory
from tests.factories.user_factory import UserFactory
from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from fastapi import HTTPException  # 🔥 Agregar este import
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


# 🔥 NUEVOS TESTS - Agregar desde aquí
def test_get_one_user_success(db_session):
    """Test para obtener un usuario por ID"""
    # Arrange
    role = RoleFactory.default()
    user = UserFactory.create()
    
    # Act
    result = UserController.get_one_user(db_session, user.id)
    
    # Assert
    assert result.id == user.id
    assert result.email == user.email
    assert result.name == user.name


def test_get_one_user_not_found(db_session):
    """Test cuando el usuario no existe"""
    # Arrange
    role = RoleFactory.default()
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.get_one_user(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_get_one_user_deleted(db_session):
    """Test que usuario eliminado no se puede obtener"""
    # Arrange
    role = RoleFactory.default()
    deleted_user = UserFactory.create(deleted_at=datetime.now(timezone.utc))
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.get_one_user(db_session, deleted_user.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
def test_update_user_success(db_session):
    """Test para actualizar un usuario exitosamente"""
    # Arrange
    role = RoleFactory.default()
    user = UserFactory.create()
    
    from schemas.users_schema import UserUpdate
    update_data = UserUpdate(
        name="Nombre Actualizado",
        email="nuevo@email.com",
        phone="666777888"
    )
    
    # Act
    result = UserController.update_user(db_session, user.id, update_data)
    
    # Assert
    assert result.id == user.id
    assert result.name == "Nombre Actualizado"
    assert result.email == "nuevo@email.com"
    assert result.phone == "666777888"


def test_update_user_not_found(db_session):
    """Test actualizar usuario que no existe"""
    # Arrange
    role = RoleFactory.default()
    
    from schemas.users_schema import UserUpdate
    update_data = UserUpdate(name="Test")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.update_user(db_session, 999, update_data)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_update_user_duplicate_email(db_session):
    """Test actualizar con email que ya existe"""
    # Arrange
    role = RoleFactory.default()
    user1 = UserFactory.create(email="user1@test.com")
    user2 = UserFactory.create(email="user2@test.com")
    
    from schemas.users_schema import UserUpdate
    update_data = UserUpdate(email="user1@test.com")  # Email de user1
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.update_user(db_session, user2.id, update_data)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already exists"


def test_update_user_partial(db_session):
    """Test actualización parcial (solo algunos campos)"""
    # Arrange
    role = RoleFactory.default()
    user = UserFactory.create(name="Original", email="original@test.com")
    
    from schemas.users_schema import UserUpdate
    update_data = UserUpdate(name="Nuevo Nombre")  # Solo actualizar nombre
    
    # Act
    result = UserController.update_user(db_session, user.id, update_data)
    
    # Assert
    assert result.name == "Nuevo Nombre"
    assert result.email == "original@test.com"  # Email no cambió
def test_delete_user_success(db_session):
    """Test para eliminar un usuario (soft delete)"""
    # Arrange
    role = RoleFactory.default()
    user = UserFactory.create()
    
    # Act
    result = UserController.delete_user(db_session, user.id)
    
    # Assert
    assert result == {"message": "User deleted successfully"}
    
    # Verificar que el usuario tiene deleted_at
    db_session.refresh(user)
    assert user.deleted_at is not None


def test_delete_user_not_found(db_session):
    """Test eliminar usuario que no existe"""
    # Arrange
    role = RoleFactory.default()
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.delete_user(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_delete_user_already_deleted(db_session):
    """Test eliminar usuario que ya fue eliminado"""
    # Arrange
    role = RoleFactory.default()
    deleted_user = UserFactory.create(deleted_at=datetime.now(timezone.utc))
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        UserController.delete_user(db_session, deleted_user.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_delete_user_and_verify_not_in_list(db_session):
    """Test que usuario eliminado no aparece en la lista"""
    # Arrange
    role = RoleFactory.default()
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    
    # Act - Eliminar user1
    UserController.delete_user(db_session, user1.id)
    
    # Assert - Solo user2 debe aparecer en la lista
    result = UserController.get_users(db_session)
    assert len(result.items) == 1
    assert result.items[0].id == user2.id