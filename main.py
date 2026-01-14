from fastapi import FastAPI

app = FastAPI()

from database import database

def run():
    pass
if __name__ == '__main__':
    database.Base.metadata.create_all(database.engine)
    run()

@app.get("/")
async def root():
    return {"message": "Hello World"}