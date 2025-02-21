from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy.orm import Session

from app.core.logging import setup_logging, log_grpc_call
from app.proto.agents.agents_grpc import AgentBase
from app.proto.agents.agents_pb2 import AgentResponse, Empty
from app.models.agent import Agent
from app.db.session import SessionLocal
from app.services.permission_service import PermissionsService, requires_permission

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
    async def Create(self, request, stream: Stream):
        """Create endpoint doesn't need permission check since anyone can create an agent"""
        request = await stream.recv_message()
        logger.info(f"creating agent: {request.name}")

        try:
            # Create the agent
            agent = Agent(
                creator_id=request.user_id,  # using user_id from request
                base_agent_id=request.base_agent_id
                if request.HasField("base_agent_id")
                else None,
                name=request.name,
                goals=request.goals if request.HasField("goals") else None,
                description=request.description
                if request.HasField("description")
                else None,
                system_prompt=request.system_prompt,
            )

            self.db.add(agent)
            self.db.flush()

            # Create initial owner membership using PermissionsService
            permissions_service = PermissionsService()
            await permissions_service.assign_role(
                agent_id=agent.id,
                assigner_id=request.user_id,
                user_id=request.user_id,
                role="owner",
            )

            self.db.commit()
            self.db.refresh(agent)

            await stream.send_message(self._to_response(agent))

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    @requires_permission(["owner", "admin", "viewer"])
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
    @requires_permission(["owner", "admin"])
    async def Update(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"updating agent: {request.agent_id}")

        try:
            agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
            if not agent:
                raise GRPCError(Status.NOT_FOUND, "Agent not found")

            # Special check for system_prompt since only owners can modify it
            if request.HasField("system_prompt"):
                permissions_service = PermissionsService()
                is_owner = await permissions_service.check_agent_permission(
                    request.user_id, request.agent_id, ["owner"]
                )
                if not is_owner:
                    raise GRPCError(
                        Status.PERMISSION_DENIED, "Only owners can modify system prompt"
                    )
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
    @requires_permission(["owner"])
    async def Delete(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"yeeting agent: {request.agent_id}")

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
