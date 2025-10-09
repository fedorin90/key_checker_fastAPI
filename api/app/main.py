from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth

app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # for frontend
    allow_credentials=True,
    allow_methods=["*"],  # allowed all methods (POST, GET, OPTIONS ...)
    allow_headers=["*"],  # allowed all headers (Authorization ...)
)
