from .perception_routes import router as perception_router
from .analytics_routes import router as analytics_router

__all__ = ["perception_router", "analytics_router"]
