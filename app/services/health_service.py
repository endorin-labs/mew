from grpclib.server import Stream
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from sqlalchemy.orm import Session
from app.proto.health.health_grpc import HealthBase
from app.db.session import SessionLocal


class HealthService(HealthBase):
    def __init__(self):
        self.db: Session = SessionLocal()

    async def Check(self, stream: Stream):
        try:
            _ = await stream.recv_message()

            self.db.execute("SELECT 1")

            await stream.send_message({"status": "healthy"})
        except Exception as e:
            raise GRPCError(Status.INTERNAL, str(e))

    def __del__(self):
        self.db.close()
