"""
AgentRed — Application Configuration
Reads all settings from environment variables.
Missing required vars raise a clear error on startup (Build Rule 12).
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import Optional
import os


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "AgentRed"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_URL_SYNC: Optional[str] = None
    DATABASE_URL_EU: Optional[str] = None
    DATABASE_URL_AP: Optional[str] = None
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── AI APIs ───────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    PRIMARY_MODEL: str = "claude-sonnet-4-6"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_MAX_TASKS_PER_CHILD: int = 100
    CELERY_WORKER_CONCURRENCY: int = 4
    MAX_CONCURRENT_SCANS: int = 10

    # ── AWS / Storage ─────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "agentred-reports"
    S3_BUCKET_EU: str = "agentred-reports-eu-west-1"
    S3_BUCKET_US: str = "agentred-reports-us-east-1"

    # ── Email ─────────────────────────────────────────────────────────────────
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@agentred.io"

    # ── Billing ───────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_STARTER_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_TEAM_PRICE_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRICE_ID: Optional[str] = None

    # ── Integrations ──────────────────────────────────────────────────────────
    SLACK_BOT_TOKEN: Optional[str] = None
    PAGERDUTY_API_KEY: Optional[str] = None
    SPLUNK_HEC_URL: Optional[str] = None
    SPLUNK_HEC_TOKEN: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None

    # ── Observability ────────────────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None
    POSTHOG_API_KEY: Optional[str] = None

    # ── Features ──────────────────────────────────────────────────────────────
    ENABLE_MONITORING: bool = True
    ENABLE_COMPLIANCE: bool = True
    ENABLE_PURPLE_TEAM: bool = True
    ENABLE_INTEL_SHARING: bool = True

    # ── Rate Limits (per plan) ────────────────────────────────────────────────
    RATE_LIMIT_FREE: int = 10        # scans/month
    RATE_LIMIT_STARTER: int = 50
    RATE_LIMIT_PRO: int = 200
    RATE_LIMIT_TEAM: int = 1000
    RATE_LIMIT_ENTERPRISE: int = 999999

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v or v == "changeme":
            raise ValueError(
                "SECRET_KEY must be set to a secure random string. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_be_set(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set. Example: postgresql+asyncpg://user:pass@host:5432/agentred")
        return v

    @model_validator(mode="after")
    def derive_sync_url(self) -> "Settings":
        if not self.DATABASE_URL_SYNC and self.DATABASE_URL:
            # Derive sync URL from async URL
            self.DATABASE_URL_SYNC = self.DATABASE_URL.replace(
                "postgresql+asyncpg://", "postgresql+psycopg2://"
            ).replace("asyncpg://", "postgresql://")
        return self

    @field_validator("ANTHROPIC_API_KEY", mode="before")
    @classmethod
    def anthropic_key_optional(cls, v) -> Optional[str]:
        return v if v and v != "sk-ant-your-key" else None

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()


# Singleton — loaded once at startup
settings = get_settings()
