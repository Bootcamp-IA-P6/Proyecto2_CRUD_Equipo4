import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from fastapi_pagination import add_pagination, Page
from fastapi_pagination.utils import disable_installed_extensions_check

from app.database.database import Base
from app.config.config_variables import settings



DATABASE_URL = (
    f"{settings.DB_DIALECT}://{settings.DB_USERNAME}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_TEST_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Crea todas las tablas al inicio y las elimina al final de la sesión de app.tests"""
    Base.metadata.create_all(bind=engine)
    
  
    disable_installed_extensions_check()
    from fastapi import FastAPI
    app = FastAPI()
    add_pagination(app)
    
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_test_database) -> Generator[Session, None, None]:
    """
    Sesión de base de datos por test con rollback automático.
    Cada test obtiene una sesión limpia.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
   
    from app.tests.factories.base_factory import set_factory_session
    set_factory_session(session)
    
    yield session

    set_factory_session(None)
    session.close()
    transaction.rollback()
    connection.close()




@pytest.fixture
def default_role(db_session):
    """Rol por defecto para usuarios"""
    from app.tests.factories.role_factory import RoleFactory
    return RoleFactory(name="user")


@pytest.fixture
def admin_role(db_session):
    """Rol de administrador"""
    from app.tests.factories.role_factory import RoleFactory
    return RoleFactory(name="admin")


@pytest.fixture
def sample_category(db_session):
    """Categoría de ejemplo"""
    from app.tests.factories.category_factory import CategoryFactory
    return CategoryFactory()


@pytest.fixture
def sample_skill(db_session):
    """Habilidad de ejemplo"""
    from app.tests.factories.skill_factory import SkillFactory
    return SkillFactory()


@pytest.fixture
def sample_user(db_session, default_role):
    """Usuario de ejemplo"""
    from app.tests.factories.user_factory import UserFactory
    return UserFactory(role=default_role)


@pytest.fixture
def sample_volunteer(db_session, sample_user):
    """Voluntario de ejemplo"""
    from app.tests.factories.volunteer_factory import VolunteerFactory
    return VolunteerFactory(user=sample_user)


@pytest.fixture
def sample_project(db_session, sample_category):
    """Proyecto de ejemplo"""
    from app.tests.factories.project_factory import ProjectFactory
    return ProjectFactory(category=sample_category)