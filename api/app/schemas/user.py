from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr


class UserOut(UserBase):
    id: int
    is_staff: bool | None = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    re_password: str

    @field_validator("re_password")
    @classmethod
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthIn(BaseModel):
    access_token: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
