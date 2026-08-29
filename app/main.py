from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    MT5ConnectionUnavailableException,
    MT5ServiceException,
    mt5_service_exception_handler,
    mt5_unavailable_exception_handler,
)
from app.core.logging import setup_logging
from app.core.mt5_manager import mt5_manager

setup_logging(debug=settings.DEBUG)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager managing startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # 1. Initialize MT5 immediately on startup
    await mt5_manager.initialize()

    # 2. Start the continuous monitoring and auto-reconnection loop
    await mt5_manager.start_monitoring()

    yield  # Application is live and serving requests

    # 3. Clean shutdown: terminate monitoring and shutdown MT5 connection
    logger.info("Application shutting down...")
    await mt5_manager.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready REST API wrapper for the MetaTrader 5 (MQL5) Python Integration.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for web and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
app.add_exception_handler(MT5ServiceException, mt5_service_exception_handler)
app.add_exception_handler(MT5ConnectionUnavailableException, mt5_unavailable_exception_handler)

# Include API Routers
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
