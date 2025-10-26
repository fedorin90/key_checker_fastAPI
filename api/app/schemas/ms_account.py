from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class MSAccountBase(BaseModel):
    email: EmailStr
    password: Optional[str] = Field(None, max_length=255, description="password")


class MSAccountCreate(MSAccountBase):
    pass


class MSAccountUpdate(BaseModel):
    email: EmailStr
    password: Optional[str] = None
    is_used: Optional[bool] = None
    usage_count: Optional[int] = None
    last_used_at: Optional[datetime] = None


class MSAccountOut(MSAccountBase):
    id: int
    is_used: Optional[bool]
    usage_count: int = 0
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
