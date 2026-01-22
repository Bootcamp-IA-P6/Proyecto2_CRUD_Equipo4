from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os

# config de Alembic
config = context.config

# logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# importar Base y engine reales
from database.database import Base, engine

# Importar todos los modelos explícitamente para que Alembic los vea
from models.users_model import User
from models.volunteers_model import Volunteer
from models.skill_model import Skill
from models.volunteer_skill_model import volunteer_skills
from models.project_model import Project
from models.project_skill_model import project_skills
from models.category_model import Category
from models.role_model import Role
from models.assignment_model import Assignment



# metadata de todos los modelos
target_metadata = Base.metadata

# OFFLINE no soportado
def run_migrations_offline():
    raise RuntimeError("Offline migrations not supported with this configuration")

# ONLINE usando tu engine real
def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # opcional: muestra SQL en consola
            compare_type=True,
            render_as_batch=True  # útil si en el futuro haces SQLite
        )

        with context.begin_transaction():
            context.run_migrations()

# Ejecuta siempre ONLINE
run_migrations_online()
