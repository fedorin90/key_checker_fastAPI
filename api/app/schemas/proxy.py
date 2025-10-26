from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import Optional


class ProxyBase(BaseModel):
    ip: constr(max_length=45) = Field(..., description="IP")
    port: int = Field(..., ge=1, le=65535, description="port")
    username: Optional[str] = Field(None, max_length=255, description="username")
    password: Optional[str] = Field(None, max_length=255, description="password")


class ProxyCreate(ProxyBase):
    pass


class ProxyUpdate(BaseModel):
    ip: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = None
    password: Optional[str] = None
    last_checked: Optional[datetime] = None
    usage_count: Optional[int] = None
    last_used_at: Optional[datetime] = None


class ProxyOut(ProxyBase):
    id: int
    last_checked: Optional[datetime]
    usage_count: int = 0
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
