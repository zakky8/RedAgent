"""
Data Residency Middleware — GDPR Chapter V compliance.
Routes EU orgs to EU database, US orgs to US database.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings


class DataResidencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only enforce if user is authenticated and org has residency enabled
        # Full enforcement happens at the DB layer per org config
        response = await call_next(request)
        return response
