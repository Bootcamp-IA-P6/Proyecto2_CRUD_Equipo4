import models
from fastapi import FastAPI
from database.database import Base, engine
from routes import volunteer_routes, users_routes


#print("MODELOS REGISTRADOS:", Base.metadata.tables.keys())
app = FastAPI()
#print(Base.metadata.tables.keys())
#Base.metadata.create_all(bind=engine)

app.include_router(users_routes.user_router)
app.include_router(volunteer_routes.router)


"""
@app.on_event("startup")
async def startup():
    users_model.Base.metadata.create_all(bind=engine)

    """