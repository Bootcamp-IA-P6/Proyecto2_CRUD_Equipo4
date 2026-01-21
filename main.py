import models
from fastapi import FastAPI
from database.database import Base, engine
from routes import volunteer_routes, users_routes, project_routes, category_routes, role_routes, skill_routes, assignment_routes
from config.logging_config import get_logger


logger = get_logger("app")
#print("MODELOS REGISTRADOS:", Base.metadata.tables.keys())
app = FastAPI()
#print(Base.metadata.tables.keys())
#Base.metadata.create_all(bind=engine)

app.include_router(users_routes.user_router)
app.include_router(volunteer_routes.router)
app.include_router(project_routes.project_router)
app.include_router(role_routes.role_router)
app.include_router(category_routes.router)
app.include_router(skill_routes.skill_router)
app.include_router(assignment_routes.assignment_router)

logger.info("Start App")


