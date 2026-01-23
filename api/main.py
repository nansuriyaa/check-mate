from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.database import create_db_and_tables
from api.routers import auth, users
import api.models # Register models

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "CheckMate API is running"}
