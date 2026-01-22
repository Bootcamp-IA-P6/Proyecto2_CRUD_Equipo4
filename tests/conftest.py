import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base 
from models import  User, Volunteer, Skill, volunteer_skills, Project, Category
from config.config_variables import settings 
from sqlalchemy.exc import OperationalError

# Construir URL de conexión usando Settings
DATABASE_URL = (
    f"{settings.DB_DIALECT}://{settings.DB_USERNAME}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{getattr(settings, 'DB_PORT', '3306')}/"
    f"{settings.DB_TEST_NAME}"
)

# Crear motor y sesión
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
@pytest.fixture(scope="function")
def db_session():
    # Crear tablas antes de cada test
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        raise RuntimeError(
            f"No se pudo conectar a la base de datos de test. "
            f"Revisa que exista '{settings.DB_TEST_NAME}' y que MySQL esté corriendo.\nError: {e}"
        )

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
