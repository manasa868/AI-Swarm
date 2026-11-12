"""FastAPI Application Main Entry Point for AI Swarm."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.session import engine, Base
from app.database import models
from app.api import projects, agents, legal, stream

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent AI Platform with Closed-Loop Testing & Transparent Legal AI",
)

# Enable CORS for local Vite development and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(agents.router, prefix=settings.API_V1_PREFIX)
app.include_router(legal.router, prefix=settings.API_V1_PREFIX)
app.include_router(stream.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    """System health and mode status endpoint."""
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "Demo Mode — simulated model response" if settings.DEMO_MODE else "Live OpenAI GPT Mode",
        "demo_mode": settings.DEMO_MODE,
        "database": settings.DATABASE_URL.split("///")[-1],
    }


# Mount generated projects and documents for easy file viewing if needed
if os.path.exists(settings.GENERATED_DIR):
    app.mount("/static/generated", StaticFiles(directory=settings.GENERATED_DIR), name="generated")
if os.path.exists(settings.DOCUMENTS_DIR):
    app.mount("/static/documents", StaticFiles(directory=settings.DOCUMENTS_DIR), name="documents")

# Mount built React frontend SPA if dist exists
FRONTEND_DIST = settings.BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend_spa")
