"""Aggregate v1 routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import authentication, health, users

router = APIRouter()
router.include_router(health.router)
router.include_router(authentication.router)
router.include_router(users.router)
