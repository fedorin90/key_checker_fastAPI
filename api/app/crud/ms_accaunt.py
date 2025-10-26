from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ms_account import MSAccount
from app.schemas.ms_account import MSAccountCreate, MSAccountUpdate


async def get_all_ms_accounts(db: AsyncSession):
    """get all ms_accounts"""
    try:
        result = await db.execute(select(MSAccount))
        return result.scalars().all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching accounts"
        ) from exc


async def get_ms_account_by_id(db: AsyncSession, ms_account_id: int) -> Optional[MSAccount]:
    """get ms_account by id"""
    result = await db.execute(select(MSAccount).where(MSAccount.id == ms_account_id))
    return result.scalars().first()


async def create_ms_account(db: AsyncSession, ms_account_data: MSAccountCreate):
    """create ms_account"""
    ms_account = MSAccount(**ms_account_data.model_dump())
    db.add(ms_account)
    try:
        await db.commit()
        await db.refresh(ms_account)
        return ms_account

    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with this email {ms_account_data.email} already exists"
        ) from exc

    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating account"
        ) from exc

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(exc)}"
        ) from exc


async def create_ms_accounts_bulk(db: AsyncSession, ms_accounts_data: List[MSAccountCreate]):
    """create list of ms_accounts"""
    ms_accounts = [MSAccount(**data.model_dump()) for data in ms_accounts_data]
    db.add_all(ms_accounts)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some accounts already exist (duplicate emails)"
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while bulk creating accounts"
        ) from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(exc)}"
        ) from exc

    for acc in ms_accounts:
        await db.refresh(acc)

    return ms_accounts


async def update_ms_account(db: AsyncSession, ms_account_id: int, ms_account_data: MSAccountUpdate) -> Optional[MSAccount]:
    """update ms_account"""
    data = ms_account_data.model_dump(exclude_unset=True)
    ms_account = await get_ms_account_by_id(db, ms_account_id)
    if not ms_account:
        raise HTTPException(status_code=404, detail="Account not found")

    for key, value in data.items():
        setattr(ms_account, key, value)

    db.add(ms_account)
    try:
        await db.commit()
        await db.refresh(ms_account)
        return ms_account
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating account"
        ) from exc


async def delete_ms_account(db: AsyncSession, ms_account_id: int) -> Optional[MSAccount]:
    """delete ms_account by id"""
    ms_account = await get_ms_account_by_id(db, ms_account_id)
    if not ms_account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        await db.delete(ms_account)
        await db.commit()
        return ms_account
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deleting account"
        ) from exc