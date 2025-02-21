from functools import wraps
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status

from app.core.logging import setup_logging
from app.models.agent_membership import AgentMembership
from app.db.session import SessionLocal

logger = setup_logging(__name__)


class AgentPermissionError(Exception):
    pass


class PermissionsService:
    def __init__(self):
        self.db: Session = SessionLocal()

    async def check_agent_permission(
        self, user_id: int, agent_id: int, required_roles: List[str]
    ) -> bool:
        membership = (
            self.db.query(AgentMembership)
            .filter(
                and_(
                    AgentMembership.user_id == user_id,
                    AgentMembership.agent_id == agent_id,
                )
            )
            .first()
        )

        if not membership:
            return False

        return membership.role in required_roles

    async def assign_role(
        self,
        agent_id: int,
        assigner_id: int,  # user doing the assigning
        user_id: int,  # user being assigned
        role: str,
    ) -> None:
        if not await self.check_agent_permission(assigner_id, agent_id, ["owner"]):
            raise AgentPermissionError("Only owners can assign roles")

        membership = (
            self.db.query(AgentMembership)
            .filter(
                and_(
                    AgentMembership.user_id == user_id,
                    AgentMembership.agent_id == agent_id,
                )
            )
            .first()
        )

        if membership:
            membership.role = role
            membership.assigned_by = assigner_id
        else:
            membership = AgentMembership(
                agent_id=agent_id, user_id=user_id, role=role, assigned_by=assigner_id
            )
            self.db.add(membership)

        self.db.commit()

    def __del__(self):
        self.db.close()


def requires_permission(required_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, stream: Stream, *args, **kwargs):
            request = await stream.recv_message()

            try:
                user_id = request.user_id
                agent_id = request.agent_id
            except AttributeError:
                raise GRPCError(
                    Status.INVALID_ARGUMENT, "Request must include user_id and agent_id"
                )

            permissions_service = PermissionsService()
            has_permission = await permissions_service.check_agent_permission(
                user_id, agent_id, required_roles
            )

            if not has_permission:
                raise GRPCError(
                    Status.PERMISSION_DENIED,
                    f"User lacks required roles: {', '.join(required_roles)}",
                )

            # Reset stream position and call the original function
            stream.reset_message()
            return await func(self, stream, *args, **kwargs)

        return wrapper

    return decorator
