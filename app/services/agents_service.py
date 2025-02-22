from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy.orm import Session

from app.core.logging import setup_logging, log_grpc_call
from app.core.auth import requires_auth, requires_permission, get_auth_context
from app.core.roles import Roles
from app.models.agent_membership import AgentMembership
from app.proto.agents.agents_grpc import AgentBase
from app.proto.agents.agents_pb2 import AgentResponse, Empty
from app.models.agent import Agent
from app.db.session import SessionLocal


logger = setup_logging(__name__)


class AgentsService(AgentBase):
    def __init__(self):
        self.db: Session = SessionLocal()

    @staticmethod
    def _to_response(agent: Agent) -> AgentResponse:
        return AgentResponse(
            id=agent.id,
            creator_id=agent.creator_id,
            base_agent_id=agent.base_agent_id,
            name=agent.name,
            goals=agent.goals,
            description=agent.description,
            system_prompt=agent.system_prompt,
            created_at=str(agent.created_at),
            updated_at=str(agent.updated_at),
        )

    @log_grpc_call(logger)
    @requires_auth()
    async def Create(self, stream: Stream):
        request = await stream.recv_message()
        auth_context = get_auth_context(stream)

        logger.info(f"creating agent: {request.name}")

        try:
            agent = Agent(
                creator_id=auth_context.user_id,
                base_agent_id=request.base_agent_id if request.HasField("base_agent_id") else None,
                name=request.name,
                goals=request.goals if request.HasField("goals") else None,
                description=request.description if request.HasField("description") else None,
                system_prompt=request.system_prompt,
            )

            self.db.add(agent)
            self.db.flush()  # to get the agent.id

            membership = AgentMembership(
                agent_id=agent.id,
                user_id=auth_context.user_id,
                role="owner",
                assigned_by=auth_context.user_id
            )
            self.db.add(membership)

            self.db.commit()
            self.db.refresh(agent)

            await stream.send_message(self._to_response(agent))

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_auth()
    @requires_permission([Roles.OWNER, Roles.ADMIN, Roles.VIEWER])
    async def Get(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"fetching agent: {request.agent_id}")

        try:
            agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
            if not agent:
                raise GRPCError(Status.NOT_FOUND, "Agent not found")

            await stream.send_message(self._to_response(agent))

        except Exception as e:
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_auth()
    @requires_permission([Roles.OWNER, Roles.ADMIN])
    async def Update(self, stream: Stream):
        request = await stream.recv_message()
        auth_context = get_auth_context(stream)
        logger.info(f"updating agent: {request.agent_id}")

        try:
            agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
            if not agent:
                raise GRPCError(Status.NOT_FOUND, "Agent not found")

            # Special check for system_prompt - only owners
            if request.HasField("system_prompt"):
                # @requires_permission already checked if user has permission
                agent.system_prompt = request.system_prompt

            # Update other fields
            if request.HasField("name"):
                agent.name = request.name
            if request.HasField("goals"):
                agent.goals = request.goals
            if request.HasField("description"):
                agent.description = request.description

            self.db.commit()
            self.db.refresh(agent)

            await stream.send_message(self._to_response(agent))

        except GRPCError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_auth()
    @requires_permission([Roles.OWNER])
    async def Delete(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"deleting agent: {request.agent_id}")

        try:
            result = self.db.query(Agent).filter(Agent.id == request.agent_id).delete()
            if not result:
                raise GRPCError(Status.NOT_FOUND, "Agent not found")

            self.db.commit()
            await stream.send_message(Empty())

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    def __del__(self):
        self.db.close()