from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.proxy import ProxyCreate, ProxyOut, ProxyUpdate
from app.crud import proxy as crud_proxy

router = APIRouter(prefix="/proxies", tags=["Proxies"])


@router.get("/", response_model=List[ProxyOut])
async def get_proxies(db: AsyncSession = Depends(get_db)):
    return await crud_proxy.get_all_proxies(db)


@router.post("/", response_model=ProxyOut, status_code=status.HTTP_201_CREATED)
async def add_proxy(proxy_data: ProxyCreate, db: AsyncSession = Depends(get_db)):
    return await crud_proxy.create_proxy(db, proxy_data)


@router.put("/{proxy_id}/", response_model=ProxyOut)
async def put_proxy(proxy_id: int, proxy_data: ProxyUpdate, db: AsyncSession = Depends(get_db)):
    proxy = await crud_proxy.update_proxy(db, proxy_id, proxy_data)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy doesn't exist")
    return proxy


@router.delete("/{proxy_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    proxy = await crud_proxy.get_proxy_by_id(db, proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy doesn't exist")
    await crud_proxy.delete_proxy(db, proxy_id)
    return None
