# tests/unit/test_user.py
from controllers.users_controller import UserController
from schemas.users_schema import UserCreate
from schemas import users_schema
from datetime import date, datetime, timezone
from tests.factories.role_factory import RoleFactory
from tests.factories.user_factory import UserFactory


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
    # Arrange: Crear rol y usuarios
    role = RoleFactory.default()  # Crea rol con ID 2
    UserFactory.create_batch(5)   # Ahora usa role_id=2
    
    # Act
    result = UserController.get_users(db_session)
    
    # Assert
    assert len(result.items) == 5
    assert result.total == 5


def test_get_users_empty(db_session):
    """Test cuando no hay usuarios"""
    # Arrange
    role = RoleFactory.default()
    
    # Act
    result = UserController.get_users(db_session)
    
    # Assert
    assert len(result.items) == 0
    assert result.total == 0


def test_get_users_excludes_deleted(db_session):
    """Test que usuarios eliminados no aparecen en la lista"""
    # Arrange
    role = RoleFactory.default()
    
    active_user = UserFactory()
    deleted_user = UserFactory(deleted_at=datetime.now(timezone.utc))  # ✅ Fix deprecation
    
    # Act
    result = UserController.get_users(db_session)
    
    # Assert
    assert len(result.items) == 1
    assert result.items[0].id == active_user.id