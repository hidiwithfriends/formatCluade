# API Routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.artists import router as artists_router
from app.routers.events import router as events_router
from app.routers.search import router as search_router

__all__ = [
    "auth_router",
    "users_router",
    "artists_router",
    "events_router",
    "search_router",
]
