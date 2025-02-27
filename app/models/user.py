from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.models import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "sanctum"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
