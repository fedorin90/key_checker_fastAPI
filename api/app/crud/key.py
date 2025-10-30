import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, status

from app.models.key import Key
from app.schemas.key import KeyCreate, KeyUpdate


async def get_keys_by_user(db: AsyncSession, user_id: int) -> List[Key]:
    """Get all user's keys"""
    try:
        result = await db.execute(select(Key).where(Key.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching keys"
        ) from exc
    

async def get_key_by_id(db: AsyncSession, key_id: int, user_id: int) -> Optional[Key]:
    """Get user's keys by ID """
    try:
      result = await db.execute(
          select(Key).where(Key.id == key_id, Key.user_id == user_id)
      )
      return result.scalars().first()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching keys"
        ) from exc



async def create_key(db: AsyncSession, key_data: KeyCreate) -> Key:
    """Create the key"""
    key = Key(**key_data.model_dump())
    db.add(key)
    try:
        await db.commit()
        await db.refresh(key)
        return key
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Key {key_data.key} already exists",
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating key",
        ) from exc


async def create_keys_bulk(db: AsyncSession, keys_data: List[KeyCreate], user_id: int) -> List[Key]:
    """Bulk create keys"""
    session_id = str(uuid.uuid4())
    created_keys = []
    skipped_keys = []

    for data in keys_data:
        key = Key(**data.model_dump(), user_id=user_id, session_id=session_id)
        db.add(key)
        try:
            await db.commit()
            await db.refresh(key)
            created_keys.append(key)
        except IntegrityError:
            await db.rollback()
            skipped_keys.append(data.key)

    return {
        "created": created_keys,
        "skipped": skipped_keys,
    }

async def get_last_session_keys(db: AsyncSession, user_id: int) -> List[Key]:
    """Get all keys by last session"""
    result = await db.execute(
        select(Key.session_id)
        .where(Key.user_id == user_id, Key.session_id.isnot(None))
        .order_by(Key.id.desc())
    )
    last_session_id = result.scalars().first()

    if not last_session_id:
        return []

    result = await db.execute(
        select(Key).where(Key.user_id == user_id, Key.session_id == last_session_id)
    )
    return result.scalars().all()


async def update_key(db: AsyncSession, key_id: int, user_id: int, key_data: KeyUpdate) -> Optional[Key]:
    """update key data"""
    key = await get_key_by_id(db, key_id, user_id)
    if not key:
        return None

    for field, value in key_data.model_dump(exclude_unset=True).items():
        setattr(key, field, value)

    db.add(key)
    await db.commit()
    await db.refresh(key)
    return key


async def delete_key(db: AsyncSession, key_id: int, user_id: int) -> bool:
    """delete key"""
    key = await get_key_by_id(db, key_id, user_id)
    if not key:
        return False

    await db.delete(key)
    await db.commit()
    return True
