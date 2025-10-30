from datetime import datetime
from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated


class KeyBase(BaseModel):
    key: Annotated[str, StringConstraints(min_length=25, max_length=25)]
    checked: Optional[bool] = False
    is_activated: Optional[bool] = None
    redeemed_by: Optional[str] = None
    redeemed_date: Optional[datetime] = None
    error_code: Optional[str] = None
    session_id: Optional[str] = None


class KeyCreate(KeyBase):

    pass


class KeyUpdate(BaseModel):
    checked: Optional[bool] = None
    is_activated: Optional[bool] = None
    redeemed_by: Optional[str] = None
    redeemed_date: Optional[datetime] = None
    error_code: Optional[str] = None
    session_id: Optional[str] = None

class KeyOut(KeyBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class KeyRead(KeyBase):
    id: int

    class Config:
        from_attributes = True
