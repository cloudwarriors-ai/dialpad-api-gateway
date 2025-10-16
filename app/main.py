from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.database.connection import engine, SessionLocal
from app.core.exceptions import CustomException
from app.services import dialpad_discovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Dialpad Platform Microservice",
    description="Microservice for Dialpad platform integrations with SSOT field mapping",
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
    return {"status": "healthy", "service": "dialpad-platform-microservice"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections and resources on startup."""
    logger.info("Initializing service...")
    # Create database tables if they don't exist
    import app.database.models  # Import models to register them with SQLAlchemy
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)

    # Initialize endpoint discovery
    dialpad_discovery.initialize_discovery()

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
from app.routers.mcp import router as mcp_router
from app.routers.transform import router as transform_router
from app.routers.proxy import router as proxy_router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
app.include_router(transform_router, prefix="/api/transform", tags=["Transform"])
app.include_router(proxy_router, tags=["Proxy"])

# Also mount the MCP router at /mcp for backward compatibility
app.include_router(mcp_router, prefix="/mcp", tags=["MCP-Legacy"])

# Discovery endpoint
@app.get("/api/discovery/dialpad-endpoints", tags=["Discovery"])
async def get_discovery_endpoints(
    category: str = None,
    limit: int = None
):
    """
    Discovery endpoint that exposes all available Dialpad API endpoints with metadata.

    Provides a queryable interface for endpoint discovery, allowing filtering by category
    and limiting result count.

    Args:
        category: Optional category filter (e.g., "Users", "Call Management")
        limit: Optional limit on number of results

    Returns:
        Dict containing endpoint metadata and list of endpoints
    """
    return dialpad_discovery.get_endpoints_by_category(category=category, limit=limit)

# Customize OpenAPI schema to include extended endpoint information
def custom_openapi():
    """
    Customize OpenAPI schema with Dialpad endpoint extensions.
    """
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Get discovered Dialpad endpoints
    dialpad_data = dialpad_discovery.fetch_dialpad_endpoints()
    endpoints = dialpad_data.get("endpoints", [])

    # Initialize paths if not present
    if 'paths' not in openapi_schema:
        openapi_schema['paths'] = {}

    # Inject discovered endpoints into standard OpenAPI paths
    for endpoint in endpoints:
        path = endpoint.get('path', '')
        method = endpoint.get('method', 'GET').lower()

        # Initialize path if not present
        if path not in openapi_schema['paths']:
            openapi_schema['paths'][path] = {}

        # Build operation object
        operation = {
            'summary': endpoint.get('summary', ''),
            'description': endpoint.get('description', ''),
            'operationId': endpoint.get('operationId', f"{method}_{path.replace('/', '_')}"),
            'tags': endpoint.get('tags', [endpoint.get('category', 'Uncategorized')]),
            'parameters': endpoint.get('parameters', []),
            'responses': {
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'}
                        }
                    }
                }
            }
        }

        # Add to paths
        openapi_schema['paths'][path][method] = operation

    # Keep x-dialpad-endpoints for backward compatibility
    openapi_schema["x-dialpad-endpoints"] = {
        "source": dialpad_data["source"],
        "endpoint_count": dialpad_data["total_endpoints"],
        "categories": dialpad_data["categories"],
        "endpoints": dialpad_data["endpoints"],
        "last_updated": dialpad_data["last_updated"]
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Override FastAPI's openapi method
app.openapi = custom_openapi

# If this file is run directly, start the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)