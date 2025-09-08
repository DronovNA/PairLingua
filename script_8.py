# Создаем оставшиеся роутеры и main.py

# Study router - ключевой для обучения
study_router = """from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.services.study_service import StudyService
from app.schemas.study import (
    StudyCardsRequest, StudyCardsResponse, 
    ReviewBatch, ReviewBatchResponse,
    SessionReplaceRequest, SessionReplaceResponse,
    StudySessionStats, LeaderboardResponse
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/cards/due",
    response_model=StudyCardsResponse,
    summary="Get cards due for review",
    description="Get cards that are due for review using spaced repetition algorithm"
)
async def get_due_cards(
    limit: int = Query(20, ge=1, le=50, description="Number of cards to return"),
    include_new: bool = Query(True, description="Include new cards"),
    exercise_types: Optional[List[str]] = Query(None, description="Filter by exercise types"),
    cefr_levels: Optional[List[str]] = Query(None, description="Filter by CEFR levels"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get cards due for review with SM-2 spaced repetition\"\"\"
    try:
        study_service = StudyService(db)
        
        request = StudyCardsRequest(
            limit=limit,
            include_new=include_new,
            exercise_types=exercise_types,
            cefr_levels=cefr_levels
        )
        
        return await study_service.get_due_cards(str(current_user.id), request)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/cards/review",
    response_model=ReviewBatchResponse,
    summary="Submit review results",
    description="Submit batch of review results and update SM-2 intervals"
)
async def submit_reviews(
    review_batch: ReviewBatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Submit review results and update spaced repetition schedule\"\"\"
    try:
        study_service = StudyService(db)
        return await study_service.submit_review_batch(str(current_user.id), review_batch)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/session/replace",
    response_model=SessionReplaceResponse,
    summary="Replace card in session",
    description="Replace a completed card with a new one in the current session"
)
async def replace_session_card(
    replace_request: SessionReplaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Replace a completed card in the current study session\"\"\"
    try:
        study_service = StudyService(db)
        return await study_service.replace_session_card(str(current_user.id), replace_request)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/session/{session_id}/stats",
    response_model=StudySessionStats,
    summary="Get session statistics",
    description="Get statistics for a specific study session"
)
async def get_session_stats(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get statistics for a study session\"\"\"
    try:
        # Implementation would fetch session stats
        # For now, return placeholder
        return StudySessionStats(
            session_id=session_id,
            started_at=datetime.utcnow(),
            cards_studied=0,
            cards_correct=0,
            average_response_time=None,
            accuracy=0.0,
            points_earned=0,
            time_spent_minutes=0
        )
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/leaderboard/weekly",
    response_model=LeaderboardResponse,
    summary="Get weekly leaderboard",
    description="Get weekly leaderboard rankings"
)
async def get_weekly_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get weekly leaderboard\"\"\"
    try:
        # Implementation would fetch leaderboard data
        # For now, return placeholder
        return LeaderboardResponse(
            entries=[],
            current_user_rank=None,
            period="weekly",
            last_updated=datetime.utcnow()
        )
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/progress/overview",
    summary="Get learning progress overview",
    description="Get overview of learning progress and upcoming reviews"
)
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get learning progress overview\"\"\"
    try:
        study_service = StudyService(db)
        
        # Get basic stats for overview
        from app.services.user_service import UserService
        user_service = UserService(db)
        stats = user_service.get_user_stats(str(current_user.id))
        
        return {
            "cards_due": stats.cards_due,
            "cards_learned": stats.cards_learned,
            "current_streak": stats.current_streak,
            "accuracy": stats.accuracy,
            "next_review_hours": 1,  # Simplified
            "study_goal_progress": min(100, (stats.cards_learned / 50) * 100)  # 50 cards goal
        }
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
"""

# Achievements router
achievements_router = """from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/",
    response_model=List[dict],
    summary="Get all achievements",
    description="Get list of all available achievements"
)
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get all available achievements\"\"\"
    try:
        achievements = db.query(Achievement).filter(
            Achievement.is_active == True
        ).all()
        
        return [
            {
                "id": achievement.id,
                "code": achievement.code,
                "title": achievement.title,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "difficulty": achievement.difficulty,
                "points": achievement.points
            }
            for achievement in achievements
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievements"
        )


@router.get(
    "/me",
    response_model=List[dict],
    summary="Get user achievements",
    description="Get achievements earned by current user"
)
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get achievements earned by current user\"\"\"
    try:
        user_achievements = db.query(UserAchievement).join(Achievement).filter(
            UserAchievement.user_id == current_user.id,
            Achievement.is_active == True
        ).all()
        
        return [
            {
                "id": ua.achievement.id,
                "code": ua.achievement.code,
                "title": ua.achievement.title,
                "description": ua.achievement.description,
                "icon": ua.achievement.icon,
                "category": ua.achievement.category,
                "difficulty": ua.achievement.difficulty,
                "points": ua.achievement.points,
                "earned_at": ua.earned_at.isoformat(),
                "context_data": ua.context_data
            }
            for ua in user_achievements
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user achievements"
        )


@router.get(
    "/progress",
    summary="Get achievement progress",
    description="Get progress towards unearned achievements"
)
async def get_achievement_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get progress towards achievements\"\"\"
    try:
        # This would calculate progress towards each achievement
        # For now, return placeholder data
        return {
            "in_progress": [
                {
                    "code": "streak_7",
                    "title": "Week Warrior",
                    "description": "Study 7 days in a row",
                    "progress": 3,
                    "target": 7,
                    "percentage": 42.8
                },
                {
                    "code": "accuracy_90",
                    "title": "Precision Master",
                    "description": "Achieve 90% accuracy over 100 reviews",
                    "progress": 67,
                    "target": 100,
                    "percentage": 67.0
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement progress"
        )
"""

# Main FastAPI application
main_py = """import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import time
import logging

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base, engine
from app.core.redis import redis_client
from app.core.exceptions import PairLinguaException
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application startup and shutdown events\"\"\"
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
        db.execute("SELECT 1")
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
"""

# Записываем файлы
with open("pairlingua/backend/app/api/v1/study.py", "w") as f:
    f.write(study_router)

with open("pairlingua/backend/app/api/v1/achievements.py", "w") as f:
    f.write(achievements_router)

with open("pairlingua/backend/app/main.py", "w", encoding="utf-8") as f:
    f.write(main_py)

# Создаем пустые __init__.py файлы
init_files = [
    "pairlingua/backend/app/api/__init__.py",
    "pairlingua/backend/app/core/__init__.py",
    "pairlingua/backend/app/services/__init__.py",
    "pairlingua/backend/app/schemas/__init__.py",
    "pairlingua/backend/app/utils/__init__.py"
]

for init_file in init_files:
    with open(init_file, "w") as f:
        f.write("")

print("✅ Study и Achievements роутеры созданы")
print("🎯 Study: due cards, reviews, sessions, leaderboard")  
print("🏆 Achievements: список, прогресс, earned")
print("🚀 Main.py с FastAPI приложением и middleware")