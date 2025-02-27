from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.core.roles import Roles
from app.models import Base


class AgentMembership(Base):
    __tablename__ = "agent_memberships"
    __table_args__ = {"schema": "sanctum"}

    agent_id = Column(
        Integer, ForeignKey("sanctum.agents.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        Integer, ForeignKey("sanctum.users.id", ondelete="CASCADE"), primary_key=True
    )

    role = Column(
        "role", Enum(Roles, name="agent_role", native_enum=True), nullable=False
    )

    assigned_by = Column(Integer, ForeignKey("sanctum.users.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def role_enum(self) -> Roles:
        return self.role

    @role_enum.setter
    def role_enum(self, role: Roles):
        self.role = role
