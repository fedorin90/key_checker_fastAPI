from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.proxy import Proxy
from app.schemas.proxy import ProxyCreate, ProxyUpdate


async def get_all_proxies(db: AsyncSession):
    """get all proxies"""
    result = await db.execute(select(Proxy))
    return result.scalars().all()


async def get_proxy_by_id(db: AsyncSession, proxy_id: int)-> Optional[Proxy]:
    """get proxy by id"""
    result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
    return result.scalars().first()


async def create_proxy(db: AsyncSession, proxy_data: ProxyCreate):
    """create proxy"""
    proxy = Proxy(**proxy_data.model_dump())
    db.add(proxy)
    await db.commit()
    await db.refresh(proxy)
    return proxy


async def update_proxy(db: AsyncSession, proxy_id: int, proxy_data: ProxyUpdate) -> Optional[Proxy]:
    """update proxy"""
    data = proxy_data.model_dump(exclude_unset=True)
    if not data:
        return await get_proxy_by_id(db, proxy_id)
    proxy = await get_proxy_by_id(db, proxy_id)
    if not proxy:
        return None

    for key, value in data.items():
        setattr(proxy, key, value)

    db.add(proxy)
    await db.commit()
    await db.refresh(proxy)
    return proxy


async def delete_proxy(db: AsyncSession, proxy_id: int) -> Optional[Proxy]:
    """delete proxy by id"""
    proxy = await get_proxy_by_id(db, proxy_id)
    if not proxy:
        return None
    await db.delete(proxy)
    await db.commit()
    return proxy
