from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship

from app.models.base import Base

class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    last_checked = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)


    accounts = relationship("MSAccount", back_populates="proxy")



    def __repr__(self):
        return f"{self.ip}:{self.port}"


    def as_playwright_dict(self):
        if self.username and self.password:
            return {
                "server": f"http://{self.ip}:{self.port}",
                "username": self.username,
                "password": self.password,
            }
        return {
            "server": f"http://{self.ip}:{self.port}",
        }
