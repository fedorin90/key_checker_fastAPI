from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.ms_account import MSAccountCreate, MSAccountOut, MSAccountUpdate
from app.crud import ms_accaunt as crud_ms_accaunt

router = APIRouter(prefix="/ms_accounts", tags=["MSAccounts"])


@router.get("/", response_model=List[MSAccountOut])
async def get_ms_account(db: AsyncSession = Depends(get_db)):
    return await crud_ms_accaunt.get_all_ms_accounts(db)


@router.post("/", response_model=MSAccountOut, status_code=status.HTTP_201_CREATED)
async def add_ms_account(ms_account_data: MSAccountCreate, db: AsyncSession = Depends(get_db)):
    return await crud_ms_accaunt.create_ms_account(db, ms_account_data)

@router.post("/bulk/", response_model=List[MSAccountOut], status_code=status.HTTP_201_CREATED)
async def add_ms_accounts_bulk(
    ms_accounts_data: List[MSAccountCreate],
    db: AsyncSession = Depends(get_db)
):
    return await crud_ms_accaunt.create_ms_accounts_bulk(db, ms_accounts_data)

@router.put("/{ms_account_id}/", response_model=MSAccountOut)
async def put_ms_account(ms_account_id: int, ms_account_data: MSAccountUpdate, db: AsyncSession = Depends(get_db)):
    ms_account = await crud_ms_accaunt.update_ms_account(db, ms_account_id, ms_account_data)
    if not ms_account:
        raise HTTPException(status_code=404, detail="ms_account doesn't exist")
    return ms_account


@router.delete("/{ms_account_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ms_account(ms_account_id: int, db: AsyncSession = Depends(get_db)):
    ms_account = await crud_ms_accaunt.get_ms_account_by_id(db, ms_account_id)
    if not ms_account:
        raise HTTPException(status_code=404, detail="ms_account doesn't exist")
    await crud_ms_accaunt.delete_ms_account(db, ms_account_id)
    return None
