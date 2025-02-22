from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.core.roles import Roles

Base = declarative_base()


class AgentMembership(Base):
    __tablename__ = "agent_memberships"
    __table_args__ = {"schema": "sanctum"}

    agent_id = Column(Integer, ForeignKey("sanctum.agents.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("sanctum.users.id", ondelete="CASCADE"), primary_key=True)

    # using the Roles enum directly now
    role = Column("role", Enum(Roles, name="agent_role", native_enum=True), nullable=False)

    assigned_by = Column(Integer, ForeignKey("sanctum.users.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # these properties aren't needed anymore since we're using the enum directly
    # but keeping them for backward compatibility
    @property
    def role_enum(self) -> Roles:
        return self.role

    @role_enum.setter
    def role_enum(self, role: Roles):
        self.role = role