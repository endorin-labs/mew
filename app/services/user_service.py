from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy.orm import Session
from app.proto.user.user_grpc import UserBase
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import SessionLocal


class UserService(UserBase):
    def __init__(self):
        self.db: Session = SessionLocal()

    async def SignUp(self, stream: Stream):
        request = await stream.recv_message()

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
            await stream.send_message(
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "name": user.name,
                    "department": user.department,
                }
            )

        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    async def Login(self, stream: Stream):
        request = await stream.recv_message()

        try:
            # find user and verify password
            user = self.db.query(User).filter(User.username == request.username).first()
            if not user or not verify_password(request.password, user.password):
                raise GRPCError(Status.UNAUTHENTICATED, "Invalid credentials")

            # create jwt token
            token = create_access_token({"user_id": user.id})

            # send back token and user data
            await stream.send_message(
                {
                    "token": token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "name": user.name,
                        "department": user.department,
                    },
                }
            )

        except GRPCError:
            raise
        except Exception as e:
            raise GRPCError(Status.INTERNAL, str(e))

    async def EditProfile(self, stream: Stream):
        request = await stream.recv_message()

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
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "name": user.name,
                    "department": user.department,
                }
            )

        except GRPCError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GRPCError(Status.INTERNAL, str(e))

    def __del__(self):
        self.db.close()
