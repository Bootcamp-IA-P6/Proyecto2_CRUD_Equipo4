from fastapi import FastAPI
from routes.project_routes import router

app = FastAPI()

#IMPORTANT: Aquí referenciamos el archivo "database" no la variable "db"
from database import database


database.Base.metadata.create_all(database.engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(router, prefix="/v1")