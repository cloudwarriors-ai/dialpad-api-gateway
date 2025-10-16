from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.database.connection import engine, SessionLocal
from app.core.exceptions import CustomException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Dialpad Platform Gateway",
    description="Gateway for Dialpad platform integrations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with actual origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

# Exception handler for custom exceptions
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "dialpad-platform-gateway"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections and resources on startup."""
    logger.info("Initializing service...")
    # Create database tables if they don't exist
    import app.database.models  # Import models to register them with SQLAlchemy
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)

    logger.info("Service initialized successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down service...")
    # Clean up any resources here
    logger.info("Service shutdown complete")

# Import and include routers
from app.routers.auth import router as auth_router
from app.routers.phone import router as phone_router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(phone_router, tags=["Dialpad Phone"])

# If this file is run directly, start the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
