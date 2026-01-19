from sqlalchemy import create_engine, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped,  mapped_column
from config.config_variables import settings
from datetime import datetime

# Variables de entorno para no exponer información sensible
DB_USER = settings.DB_USERNAME
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_DEV_NAME = settings.DB_DEV_NAME


# database url
#DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_DEV_NAME}"

# Crea un engine
#engine = create_engine(DATABASE_URL)



engine = create_engine(
    "mysql+pymysql://",  # dejamos la URL vacía
    connect_args={
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_DEV_NAME,
        "port": int(3306)
    }
)

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )

# Crea una clase para configurar la sesión
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase base para los modelos
#Base = declarative_base()

# función para obtener la sesión de la base de datos
def get_db():
    db = Session()  # Crea una nueva sesión
    try:
        yield db  # Usa la sesión
    finally:
        db.close()  # Cierra la sesión al terminar

