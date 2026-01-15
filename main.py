from fastapi import FastAPI
from routes import users_routes
from database.database import engine
from models import users_model


app = FastAPI()

# from database import database

# def run():
#     pass
# if __name__ == '__main__':
#     database.Base.metadata.create_all(bind=database.engine)
#     run()
    
@app.on_event("startup")
async def startup():
    users_model.Base.metadata.create_all(bind=engine)

app.include_router(users_routes.user_router)