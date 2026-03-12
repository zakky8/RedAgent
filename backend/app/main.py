"""
AgentRed — FastAPI Application Entry Point
Build Rule 7: Health check endpoint at /health
Build Rule 12: Missing env vars raise clear errors on startup
"""
import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.database import check_db_connection, init_pgvector, engine, Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"Starting AgentRed {settings.VERSION} in {settings.ENVIRONMENT} mode")

    # Initialize Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
        )
        logger.info("Sentry initialized")

    # Init database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_pgvector()

    db_ok = await check_db_connection()
    if not db_ok:
        raise RuntimeError("Database connection failed on startup")

    logger.info("AgentRed started successfully")
    yield

    # Cleanup
    await engine.dispose()
    logger.info("AgentRed shutting down")


app = FastAPI(
    title="AgentRed API",
    description="World's most comprehensive AI Red Teaming Platform — 456 attacks, 214 features, 47 categories",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import data residency middleware
from app.core.data_residency import DataResidencyMiddleware
app.add_middleware(DataResidencyMiddleware)


# Include API router
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ── Health Check (Build Rule 7) ────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/", tags=["health"])
async def root():
    return {"message": "AgentRed API", "version": settings.VERSION, "docs": "/docs"}


# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
