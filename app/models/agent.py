from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = {"schema": "sanctum"}  # keeping it consistent w/ users table

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("sanctum.users.id"), nullable=False)
    base_agent_id = Column(
        Integer, ForeignKey("sanctum.agents.id", ondelete="SET NULL")
    )

    # these fields get encrypted w/ the kms key
    name = Column(String(255), nullable=False)
    goals = Column(Text)
    description = Column(Text)
    system_prompt = Column(Text)

    # for encryption/decryption of the above fields
    kms_key = Column(String(255), nullable=False)

    # timestamps bc why not
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
