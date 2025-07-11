import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.api.routes import voice, health

logger = logging.getLogger(__name__)
setup_logging()

app = FastAPI(
    title="ASP Bot API",
    description="Bulgarian-language AI assistant for the Agency for Social Assistance in Bulgaria",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting ASP Bot API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ASP Bot API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )