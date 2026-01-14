import models
from fastapi import FastAPI
from database.database import Base, engine
#from models.volunteers_model import Volunteer
from routes.volunteer_routes import router as volunteer_router


print("MODELOS REGISTRADOS:", Base.metadata.tables.keys())



app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(volunteer_router)
@app.get("/")
def root():
    return {"status": "API funcionando"}