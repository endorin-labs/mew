from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy.orm import Session

from app.core.logging import setup_logging, log_grpc_call
from app.proto.user.user_grpc import UserBase
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import SessionLocal
from app.proto.user.user_pb2 import UserResponse, LoginResponse

logger = setup_logging(__name__)


class UserService(UserBase):
    def __init__(self):
        self.db: Session = SessionLocal()

    @log_grpc_call(logger)
    async def SignUp(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"signing up user: {request.email}")
        try:
            # hash the password and create user
            hashed = hash_password(request.password)
            user = User(
                email=request.email,
                username=request.username,
                name=request.name,
                department=request.department,
                password=hashed,
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # send back the user data (excluding password)
            response = UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                name=user.name,
                department=user.department,
            )
            await stream.send_message(response)

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    async def Login(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"logging in user: {request.username}")
        try:
            # find user and verify password
            user = self.db.query(User).filter(User.username == request.username).first()
            if not user or not verify_password(request.password, user.password):
                raise GRPCError(Status.UNAUTHENTICATED, "Invalid credentials")

            # create jwt token
            token = create_access_token({"user_id": user.id})

            # send back token and user data
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                name=user.name,
                department=user.department,
            )
            response = LoginResponse(token=token, user=user_response)
            await stream.send_message(response)

        except GRPCError:
            raise
        except Exception as e:
            raise GRPCError(Status.INTERNAL, str(e))

    @log_grpc_call(logger)
    async def EditProfile(self, stream: Stream):
        request = await stream.recv_message()
        logger.info(f"editing profile for: {request.email}")
        try:
            # find and update user
            user = self.db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise GRPCError(Status.NOT_FOUND, "User not found")

            user.email = request.email
            user.username = request.username
            user.name = request.name
            user.department = request.department

            self.db.commit()
            self.db.refresh(user)

            # send back updated user data
            await stream.send_message(
                UserResponse(
                    **{
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "name": user.name,
                        "department": user.department,
                    }
                )
            )

        except GRPCError as e:
            logger.error(f"encountered error: {e}")
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    def __del__(self):
        self.db.close()
