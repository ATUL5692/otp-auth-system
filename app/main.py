from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.db import models 

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API running"}

# create tables
Base.metadata.create_all(bind=engine)