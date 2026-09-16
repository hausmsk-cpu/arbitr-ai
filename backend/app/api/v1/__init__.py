"""API v1 — маршруты."""

from fastapi import APIRouter

from app.api.v1 import auth, cases, requests, users, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(ai.router, tags=["ai"])