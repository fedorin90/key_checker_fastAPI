from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from app.core.config import settings
from app.api.v1 import auth, task_router, proxy_router, ms_account_router, key_router

app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(auth.router)
app.include_router(task_router.router)
app.include_router(proxy_router.router)
app.include_router(ms_account_router.router)
app.include_router(key_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # for frontend
    allow_credentials=True,
    allow_methods=["*"],  # allowed all methods (POST, GET, OPTIONS ...)
    allow_headers=["*"],  # allowed all headers (Authorization ...)
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Incorrect data"},
    )
