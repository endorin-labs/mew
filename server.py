import asyncio
from grpclib.server import Server
from grpclib.utils import graceful_exit
from app.services.user_service import UserService
from app.core.logging import setup_logging

logger = setup_logging(__name__)


async def start_server():
    server = Server([UserService()])

    with graceful_exit([server]):
        await server.start("0.0.0.0", 50051)
        logger.info("gRPC Server started on port 50051")

        await server.wait_closed()


def serve():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        loop.close()


if __name__ == "__main__":
    serve()
