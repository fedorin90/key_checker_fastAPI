from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from app.models.base import Base


class MSAccount(Base):
    __tablename__ = "MS_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

    proxy_id = Column(Integer, ForeignKey("proxies.id", ondelete="SET NULL"), nullable=True)
    proxy = relationship("Proxy", back_populates="accounts")



    def __repr__(self):
        return self.email
