from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os

# Alembic config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar Base
from app.database.database import Base

# Importar modelos (OBLIGATORIO)
from app.models.users_model import User
from app.models.volunteers_model import Volunteer
from app.models.skill_model import Skill
from app.models.volunteer_skill_model import volunteer_skills
from app.models.project_model import Project
from app.models.project_skill_model import project_skills
from app.models.category_model import Category
from app.models.role_model import Role
from app.models.assignment_model import Assignment

# Metadata
target_metadata = Base.metadata

# ONLINE usando tu engine real
def run_migrations_online():
    # Construir URL desde ENV (Docker-friendly)
    db_url = (
        f"{os.getenv('DB_DIALECT')}+pymysql://"
        f"{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_DEV_NAME')}"
    )

    config.set_main_option("sqlalchemy.url", db_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations not supported")
else:
    run_migrations_online()
