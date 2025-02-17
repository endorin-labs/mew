from fastapi import FastAPI
from app.core.logging import setup_logging, LoggingMiddleware
from app.api.routes import health

logger = setup_logging(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="mew - a KB enrichment API")

    app.add_middleware(LoggingMiddleware)

    app.include_router(health.router, tags=["health"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
