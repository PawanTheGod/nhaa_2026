from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes.cases import router as cases_router
from app.routes.risk_assessments import router as ra_router
from app.routes.websocket import router as ws_router
from app.routes.stats import router as stats_router
from app.routes.notifications import router as notifications_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import AsyncSessionLocal, engine, Base
    import app.models  # noqa: F401 — ensure all models are registered

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()


app = FastAPI(
    title="NHAA Central Case API",
    description=(
        "Single shared PostgreSQL-backed API for the NHAA (14566) Helpline AI Triage System.\n\n"
        "**Channels:** Portal, Chatbot, IVRS, Mobile App\n\n"
        "Every complaint lands in the SAME central case database and goes through the SAME AI pipeline.\n"
        "This is the foundation of the project -- do not bypass these endpoints."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.include_router(cases_router, prefix="/api")
app.include_router(ra_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nhaa-case-api"}


@app.get("/")
async def root():
    return {"service": "NHAA Central Case API", "docs": "/docs"}
