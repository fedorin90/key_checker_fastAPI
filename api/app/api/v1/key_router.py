import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc
from app.core.db import get_db
from app.models.key import Key
from app.schemas.key import KeyCreate, KeyOut, KeyUpdate, KeyRead
from app.crud import key as crud_key
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/keys", tags=["Keys"])


@router.post("/", response_model=List[KeyRead])
async def create_keys_route(
    key_objects: List[KeyCreate],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Save list of keys for current user
    Every load = new session.
    """
    if not key_objects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid keys provided"
        )

    # new session_id for this load
    session_id = str(uuid.uuid4())

    new_keys = [
        Key(
            key=obj.key,
            user_id=current_user.id,
            session_id=session_id
        )
        for obj in key_objects
    ]

    db.add_all(new_keys)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some keys already exist"
        ) from exc

    await db.refresh(new_keys[0])  # retern actual data

    return new_keys

@router.get("/last/", response_model=List[KeyRead])
async def get_last_session_keys(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all keys from the latest session of the current user.
    """
    # Найдём последнюю session_id пользователя
    result = await db.execute(
        select(Key.session_id)
        .where(Key.user_id == current_user.id)
        .order_by(desc(Key.id))
        .limit(1)
    )
    last_session = result.scalar_one_or_none()

    if not last_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found for this user"
        )

    # Получим все ключи этой сессии
    result = await db.execute(
        select(Key)
        .where(Key.user_id == current_user.id, Key.session_id == last_session)
        .order_by(Key.id)
    )
    keys = result.scalars().all()

    return keys