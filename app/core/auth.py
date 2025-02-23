# app/core/auth.py
from dataclasses import dataclass
from functools import wraps
from typing import List, Optional
import jwt
from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.roles import Roles
from app.models.agent_membership import AgentMembership
from app.db.session import SessionLocal
from app.core.logging import setup_logging

logger = setup_logging(__name__)


@dataclass
class AuthContext:
    user_id: int
    agent_id: Optional[int] = None  # Some endpoints might not need an agent_id


def validate_auth(stream: Stream) -> AuthContext:
    try:
        metadata = dict(stream.metadata)

        auth_header = metadata.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise GRPCError(Status.UNAUTHENTICATED, "Missing or invalid auth token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            raise GRPCError(Status.UNAUTHENTICATED, "Invalid auth token")

        agent_id = metadata.get("agent-id")
        if agent_id:
            try:
                agent_id = int(agent_id)
            except ValueError:
                raise GRPCError(Status.INVALID_ARGUMENT, "agent-id must be an integer")

        return AuthContext(user_id=user_id, agent_id=agent_id)

    except Exception as e:
        logger.error(f"Auth validation error: {str(e)}")
        raise GRPCError(Status.INTERNAL, str(e))


def check_permission(
    user_id: int, agent_id: int, required_roles: List[Roles], db: Session
) -> bool:
    membership = (
        db.query(AgentMembership)
        .filter(
            and_(
                AgentMembership.user_id == user_id,
                AgentMembership.agent_id == agent_id,
            )
        )
        .first()
    )
    return membership is not None and membership.role in required_roles


def requires_auth(skip_auth: bool = False, require_agent: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(service, stream: Stream, *args, **kwargs):
            if skip_auth:
                return await func(service, stream, *args, **kwargs)

            auth_context = validate_auth(stream)

            if require_agent and auth_context.agent_id is None:
                raise GRPCError(
                    Status.INVALID_ARGUMENT, "agent-id is required in metadata"
                )

            stream.auth_context = auth_context

            return await func(service, stream, *args, **kwargs)

        return wrapper

    return decorator


def requires_permission(required_roles: List[Roles]):
    def decorator(func):
        @wraps(func)
        async def wrapper(service, stream: Stream, *args, **kwargs):
            auth_context = getattr(stream, "auth_context", None)
            if not auth_context:
                raise GRPCError(Status.UNAUTHENTICATED, "No auth context found")

            if auth_context.agent_id is None:
                raise GRPCError(
                    Status.INVALID_ARGUMENT, "agent-id is required in metadata"
                )

            db = SessionLocal()
            try:
                has_permission = check_permission(
                    auth_context.user_id, auth_context.agent_id, required_roles, db
                )

                if not has_permission:
                    role_names = [role.name for role in required_roles]
                    raise GRPCError(
                        Status.PERMISSION_DENIED,
                        f"User lacks required roles: {', '.join(role_names)}",
                    )

                return await func(service, stream, *args, **kwargs)
            finally:
                db.close()

        return wrapper

    return decorator


def get_auth_context(stream: Stream) -> Optional[AuthContext]:
    return getattr(stream, "auth_context", None)
