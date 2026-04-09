from fastapi import FastAPI
from db import engine, Base
import models
from auth import router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)