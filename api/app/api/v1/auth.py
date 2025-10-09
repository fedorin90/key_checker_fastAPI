# app/api/auth.py
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserOut, TokenOut, GoogleAuthIn, LoginIn
from app.crud import user as crud_user
from app.core.config import settings
from app.core.security import create_access_token, create_activation_token
from app.core.db import get_db
from app.models.user import User
from app.utils.email_utils import send_activation_email

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ========== REGISTER ==========
@router.post("/register/")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_user.get_user_by_email(db, user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await crud_user.create_user(db, user_in)

    # create a token and send email
    token = create_activation_token({"sub": user.email})
    send_activation_email(user.email, token)
    return {"message": "Please check your email to activate your account"}


# ========== LOGIN ==========
@router.post("/login/", response_model=TokenOut)
async def login_json(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await crud_user.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ========== GOOGLE LOGIN ==========
@router.post("/google/", response_model=TokenOut)
async def google_login(data: GoogleAuthIn, db: AsyncSession = Depends(get_db)):
    google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={data.access_token}"
    resp = requests.get(google_url)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    payload = resp.json()
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        user = await crud_user.create_user_google(db, email=email)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


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


# ========== LOGOUT ==========
@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"message": "Logged out successfully"}

#========== PROFILE ==========
@router.get("/me/", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

#========== ACTIVATION ==========
@router.get("/activate/{token}")
async def activate_user(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Activation token expired")

    user = await crud_user.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        return {"message": "User already activated"}

    user.is_active = True
    await db.commit()
    return {"message": "Account activated successfully!"}


#========== REACTIVATION ==========
@router.post("/resend-activation/")
async def resend_activation(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    email = data.get("email")

    user = await crud_user.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="User already activated")

    token = create_activation_token({"sub": email})
    send_activation_email(email, token)

    return {"message": "New activation link sent to your email."}
