import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import time
import logging

from sqlalchemy import text
from app.core.config import settings
from app.core.database import Base, engine
from app.core.redis import redis_client
from app.core.exceptions import PairLinguaException
from app.api.v1.router import api_router

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting PairLingua API...")
    
    try:
        # Test database connection
        Base.metadata.create_all(bind=engine)
        logger.info("📊 Database connected")
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("🔥 Redis connected")
        
        logger.info("✅ PairLingua API started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down PairLingua API...")
    try:
        await redis_client.close()
        logger.info("✅ PairLingua API shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Interactive language learning application with spaced repetition",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # адрес вашего фронтенда
    allow_credentials=True,
    allow_methods=["*"],  # все методы разрешены
    allow_headers=["*"],  # все заголовки разрешены
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["pairlingua.com", "*.pairlingua.com"]
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(PairLinguaException)
async def pairlingua_exception_handler(request: Request, exc: PairLinguaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": None,
                "trace_id": getattr(request.state, "trace_id", None)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None,
                "trace_id": getattr(request.state, "trace_id", None)
            }
        }
    )


# Health check endpoint
@app.get(
    "/api/v1/health",
    tags=["health"],
    summary="Health check",
    description="Check API health status"
)
async def health_check():
    try:
        # Test database
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Test Redis
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Metrics endpoint for Prometheus
@app.get(
    "/api/v1/metrics",
    tags=["monitoring"],
    summary="Prometheus metrics",
    description="Get Prometheus metrics"
)
async def get_metrics():
    # In production, this would return actual Prometheus metrics
    return JSONResponse(content={"message": "Metrics endpoint - implement Prometheus metrics"})


# Include API routes
app.include_router(
    api_router,
    prefix="/api/v1"
)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Info",
    description="Get API information"
)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_url": "/api/v1/health"
    }


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Interactive language learning with spaced repetition algorithm",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
