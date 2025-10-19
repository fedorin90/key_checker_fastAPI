from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()



async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_pw = pwd_context.hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        is_active=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_user_google(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def update_user_password(db: AsyncSession, user: User, hashed_password: str):
    user.hashed_password = hashed_password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
