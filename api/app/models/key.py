from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(25))
    checked = Column(Boolean, default=False)
    is_activated = Column(Boolean, default=False, nullable=True)
    redeemed_by = Column(String, nullable=True)
    redeemed_date = Column(DateTime, nullable=True)
    error_code = Column(String, nullable=True)
    session_id = Column(String(36), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="keys")

    def __repr__(self):
        return self.key
