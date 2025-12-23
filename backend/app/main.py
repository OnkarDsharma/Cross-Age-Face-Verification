from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import connect_to_mongo, close_mongo_connection
from .auth.router import router as auth_router
from .verification.router import router as verify_router
from .config import settings
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Face Verification API")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    logger.info("✓ Database connected")
    
    # Log configuration
    logger.info(f"✓ DeepFace model: {settings.DEEPFACE_MODEL}")
    logger.info(f"✓ Verification threshold: {settings.VERIFICATION_THRESHOLD}")
    logger.info(f"✓ Environment: {'Production' if os.getenv('SPACE_ID') else 'Development'}")
    
    logger.info("✓ Application startup complete")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("✓ Application shutdown complete")

app = FastAPI(
    title="Cross-Age Face Verification API",
    description="API for verifying faces across different ages using DeepFace",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - UPDATE WITH YOUR NETLIFY URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://earnest-treacle-9f76c3.netlify.app",  # Will be updated with actual URL
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(verify_router)

@app.get("/")
async def root():
    return {
        "message": "Cross-Age Face Verification API",
        "version": "2.0.0",
        "status": "running",
        "model": settings.DEEPFACE_MODEL,
        "threshold": settings.VERIFICATION_THRESHOLD,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": settings.DEEPFACE_MODEL
    }