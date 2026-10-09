import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.api.auth_router import router as auth_router
from backend.app.api.predict_router import router as predict_router
from backend.app.api.sources_router import router as sources_router
from backend.app.api.reports_router import router as reports_router
from backend.app.api.alerts_router import router as alerts_router
from backend.app.api.analytics_router import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables if not present
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AquaShield AI - AI-Powered Water Quality Monitoring & Safe Source Locator API",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for report photo uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 1. Mount API V1 prefixed routes
api_prefix = settings.API_V1_STR # "/api"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(predict_router, prefix=api_prefix)
app.include_router(sources_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(analytics_router, prefix=api_prefix)

# 2. Also mount root aliases (/predict, /sources, /reports, /alerts) for direct REST access
app.include_router(predict_router)
app.include_router(sources_router)
app.include_router(reports_router)
app.include_router(alerts_router)

@app.get("/", tags=["Health"])
async def root_health():
    return {
        "status": "healthy",
        "service": "AquaShield AI API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
