from fastapi import FastAPI
from db import Base, engine
from auth import router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)


# Health Check
@app.get("/")
def health():
    return {"status": "running"}