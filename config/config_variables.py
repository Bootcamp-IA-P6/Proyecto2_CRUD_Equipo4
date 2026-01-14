import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

class Settings:
    DB_USERNAME: str = os.getenv("DB_USERNAME","root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_DEV_NAME", "volunteers")
    DB_TEST_NAME: str = os.getenv("DB_TEST_NAME", "volunteer_test")


settings = Settings()