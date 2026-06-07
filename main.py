from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.cors import setup_cors
from app.routers import (
    ai,
    analytics,
    confirmation,
    events,
    hands,
    health,
    merchants,
    nail_tryon,
    recommendation,
    styles,
    tryon,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Nail Try-on Backend",
        version="0.1.0",
        description="AI 美甲试戴与智能运营系统后端 MVP",
    )

    setup_cors(app)

    settings.ensure_directories()
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

    app.include_router(health.router)
    app.include_router(styles.router)
    app.include_router(events.router)
    app.include_router(analytics.router)
    app.include_router(tryon.router)
    app.include_router(ai.router)
    app.include_router(hands.router)
    app.include_router(merchants.router)
    app.include_router(recommendation.router)
    app.include_router(confirmation.router)
    app.include_router(nail_tryon.router)
    return app


app = create_app()
