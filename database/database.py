from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config_variables import settings

# Variables de entorno para no exponer información sensible
DB_USER = settings.DB_USERNAME
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_DEV_NAME = settings.DB_DEV_NAME

# Conexión con la base de datos
DATABASE_URL = "mysql+pymysql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+"/"+DB_DEV_NAME+""  # MySQL

# Crea un engine
engine = create_engine(DATABASE_URL)

# Crea una clase para configurar la sesión
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase base para los modelos
Base = declarative_base()

# función para obtener la sesión de la base de datos
def get_db():
    db = Session()  # Crea una nueva sesión
    try:
        yield db  # Usa la sesión
    finally:
        db.close()  # Cierra la sesión al terminar


