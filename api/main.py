from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.database import create_db_and_tables
from api.routers import auth, users, frontend
import api.models # Register models

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(frontend.router)
from api.routers import check
app.include_router(check.router)


