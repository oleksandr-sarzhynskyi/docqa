from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.collections import router as collections_router
from app.api.documents import router as documents_router
from app.api.query import router as query_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application..")
    yield
    print("Shutting down application..")


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(collections_router)
app.include_router(documents_router)
app.include_router(query_router)