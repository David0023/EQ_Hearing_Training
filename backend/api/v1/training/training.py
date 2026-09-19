from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.training_session import (
    TrainingSessionCreateRequest, 
    TrainingSessionCreateResponse,
    GetTrainingSessionWithQuestionsResponse,
    GetAllTrainingSessionsResponse
)
from schemas.training_question import GetTrainingQuestionResponse

from services.training import create_training_session, create_training_question
from core.dependencies import get_db, get_current_user
from models.user import User
from models.training_session import TrainingSession
from repositories.training_session import (
    get_one_training_session, get_training_sessions, get_one_training_session_with_questions
)

from api.v1.training.question import router as question_router
from api.v1.training.session import router as session_router

router = APIRouter(
    prefix='/training',
    tags=['training']
)

router.include_router(question_router)
router.include_router(session_router)
