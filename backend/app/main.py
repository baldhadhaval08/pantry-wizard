"""FastAPI application main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.database import init_db
from app.routers import users, pantry, recipes, history

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="PantryWizard+ API",
    description="AI Health & Recipe Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
images_dir = static_dir / "images"
images_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(pantry.router, prefix=settings.API_V1_PREFIX)
app.include_router(recipes.router, prefix=settings.API_V1_PREFIX)
app.include_router(history.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PantryWizard+ API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

