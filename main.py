"""
CYBERAI — Full Stack AI Cybersecurity Platform
Main FastAPI Application Entry Point
"""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.routers import auth, chat, security, admin

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite database and models
    init_db()
    yield
    # Shutdown events if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional AI Cybersecurity Assistant, Static Code Analyzer, and Website Security Checker",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(security.router)
app.include_router(admin.router)


# Health check endpoint
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL
    }


# Serve Frontend Static Assets (CSS and JS)
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


# Frontend HTML Page Routes
@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/login", include_in_schema=False)
def serve_login():
    return FileResponse(str(FRONTEND_DIR / "login.html"))


@app.get("/register", include_in_schema=False)
def serve_register():
    return FileResponse(str(FRONTEND_DIR / "register.html"))


@app.get("/analyzer", include_in_schema=False)
def serve_analyzer():
    return FileResponse(str(FRONTEND_DIR / "analyzer.html"))


@app.get("/scanner", include_in_schema=False)
def serve_scanner():
    return FileResponse(str(FRONTEND_DIR / "scanner.html"))


@app.get("/admin", include_in_schema=False)
def serve_admin():
    return FileResponse(str(FRONTEND_DIR / "admin.html"))


# Global 404 handler for unknown API routes vs frontend routes
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "So'ralgan API resursi topilmadi (Endpoint not found)"}
        )
    return FileResponse(str(FRONTEND_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
