"""
API v1 router configuration.

This module sets up the main API router and includes all endpoint routers
for version 1 of the API.
"""

from fastapi import APIRouter

from app.api.v1 import receipts

# Create the main API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(receipts.router)