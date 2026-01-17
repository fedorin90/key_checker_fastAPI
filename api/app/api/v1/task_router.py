from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from celery.result import AsyncResult
from app.core.db import get_db
from app.models.key import Key
from app.models.user import User
from app.core.config import settings
from app.core.celery_app import celery
from pydantic import BaseModel
from app.tasks.check_keys_task import check_keys_task
import redis
from app.api.v1.auth import get_current_user


router = APIRouter()

# Подключение к Redis для хранения task_id по session_id
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

class ProgressResponse(BaseModel):
    task_id: str
    status: str
    ready: bool
    session_id: str | None = None
    total: int | None = None
    checked: int | None = None
    percent: float | None = None
    remaining: int | None = None


@router.get("/check_and_progress/{session_id}", response_model=ProgressResponse)
async def check_and_progress(session_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Если таска ещё не запущена - создаём её.
    И возвращаем прогресс: task_id, status, checked, total, percent.
    """

    # Проверяем, есть ли task_id в Redis для этой сессии
    task_id = redis_client.get(f"task:{session_id}")

    if task_id:
        # таска уже есть, получаем прогресс
        result = AsyncResult(task_id, app=celery)
        status = result.status
    else:
        # создаём новую таску
        task = check_keys_task.delay(session_id)
        task_id = task.id
        status = "STARTED"
        # сохраняем task_id в Redis
        redis_client.set(f"task:{session_id}", task_id)

    # Получаем прогресс из базы
    total_result = await db.execute(
        select(func.count(Key.id)).where(Key.session_id == session_id, Key.user_id == current_user.id) # pylint: disable=not-callable
    )
    total = total_result.scalar_one_or_none() or 0

    checked_result = await db.execute(
        select(func.count(Key.id)).where( # pylint: disable=not-callable
            Key.session_id == session_id,
            Key.user_id == current_user.id,
            Key.checked.is_(True),
        )
    )
    checked = checked_result.scalar_one_or_none() or 0
    percent = round(100 * checked / total, 2) if total else 0

    return ProgressResponse(
        task_id=task_id,
        status=status,
        ready=status in ("SUCCESS", "FAILURE"),
        session_id=session_id,
        total=total,
        checked=checked,
        percent=percent,
        remaining=total - checked if total else None,
    )
