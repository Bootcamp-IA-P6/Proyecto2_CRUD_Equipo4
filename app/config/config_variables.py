import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

class Settings:
    DB_USERNAME: str = os.getenv("DB_USERNAME", "default_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "valor_por_defecto")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_DEV_NAME: str = os.getenv("DB_DEV_NAME", "volunteer_crud")
    DB_TEST_NAME: str = os.getenv("DB_TEST_NAME", "volunteer_crud_test")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_DIALECT: str = os.getenv("DB_DIALECT", "mysql+pymysql")  ###he agregado estas dos variales para centralizarlo todo en este archivo

    API_URL: str = os.getenv("API_BASE_URL","api_base_url")


settings = Settings() 