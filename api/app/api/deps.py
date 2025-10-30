
from fastapi import Depends, HTTPException
from fastapi.security import  OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user as crud_user
from app.core.config import settings

from app.core.db import get_db
from app.models.user import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form/")



# ========== GET CURRENT USER ==========
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await crud_user.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
