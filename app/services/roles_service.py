from grpclib.const import Status
from grpclib.exceptions import GRPCError
from grpclib.server import Stream
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.auth import requires_auth, requires_permission, get_auth_context
from app.core.logging import setup_logging, log_grpc_call
from app.core.roles import Roles
from app.db.session import SessionLocal
from app.models.agent_membership import AgentMembership
from app.proto.roles.roles_grpc import RolesBase
from app.proto.roles.roles_pb2 import RoleResponse, ListMembersResponse, MemberInfo

logger = setup_logging(__name__)


class RolesService(RolesBase):
    def __init__(self):
        self.db: Session = SessionLocal()

    @log_grpc_call(logger)
    @requires_auth(require_agent=True)
    @requires_permission(
        [Roles.OWNER, Roles.ADMIN]
    )  # only owners/admins can assign roles
    async def AssignRole(self, stream: Stream):
        request = await stream.recv_message()
        auth_context = get_auth_context(stream)

        try:
            # check if membership already exists
            existing = (
                self.db.query(AgentMembership)
                .filter(
                    and_(
                        AgentMembership.agent_id == auth_context.agent_id,
                        AgentMembership.user_id == request.user_id,
                    )
                )
                .first()
            )

            if existing:
                # update existing role
                existing.role = request.role
                existing.assigned_by = auth_context.user_id
            else:
                # create new membership
                membership = AgentMembership(
                    agent_id=auth_context.agent_id,
                    user_id=request.user_id,
                    role=request.role,
                    assigned_by=auth_context.user_id,
                )
                self.db.add(membership)

            self.db.commit()

            await stream.send_message(
                RoleResponse(success=True, message="Role assigned successfully")
            )

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_auth(require_agent=True)
    @requires_permission([Roles.OWNER, Roles.ADMIN, Roles.VIEWER])
    async def ListMembers(self, stream: Stream):
        auth_context = get_auth_context(stream)

        try:
            members = (
                self.db.query(AgentMembership)
                .filter(AgentMembership.agent_id == auth_context.agent_id)
                .all()
            )

            member_infos = [
                MemberInfo(
                    user_id=member.user_id,
                    role=member.role,
                    assigned_by=member.assigned_by,
                    assigned_at=str(member.assigned_at),
                )
                for member in members
            ]

            await stream.send_message(ListMembersResponse(members=member_infos))

        except Exception as e:
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_auth(require_agent=True)
    @requires_permission(
        [Roles.OWNER, Roles.ADMIN]
    )  # only owners/admins can revoke roles
    async def RevokeRole(self, stream: Stream):
        request = await stream.recv_message()
        auth_context = get_auth_context(stream)

        try:
            # first check if we're trying to revoke the last owner
            if request.role == "OWNER":
                owner_count = (
                    self.db.query(AgentMembership)
                    .filter(
                        and_(
                            AgentMembership.agent_id == auth_context.agent_id,
                            AgentMembership.role == "OWNER",
                        )
                    )
                    .count()
                )

                if owner_count <= 1:
                    raise GRPCError(
                        Status.FAILED_PRECONDITION,
                        "Cannot revoke the last owner's role",
                    )

            # delete the membership
            result = (
                self.db.query(AgentMembership)
                .filter(
                    and_(
                        AgentMembership.agent_id == auth_context.agent_id,
                        AgentMembership.user_id == request.user_id,
                    )
                )
                .delete()
            )

            if not result:
                raise GRPCError(Status.NOT_FOUND, "Membership not found")

            self.db.commit()

            await stream.send_message(
                RoleResponse(success=True, message="Role revoked successfully")
            )

        except GRPCError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    def __del__(self):
        self.db.close()
