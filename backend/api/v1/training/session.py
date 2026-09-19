from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.training_session import (
    TrainingSessionCreateRequest, 
    TrainingSessionCreateResponse,
    GetTrainingSessionWithQuestionsResponse,
    GetAllTrainingSessionsResponse
)

from services.training import create_training_session
from core.dependencies import get_db, get_current_user
from models.user import User
from repositories import training_session

router = APIRouter(
    prefix='/session',
    tags=['session']
)
    
##---------------------------------------
@router.get('/{session_id}', 
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingSessionWithQuestionsResponse
)
async def get_single_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = await training_session.get_one_with_questions(db, id=session_id)

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")

    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")

    return session

@router.get('/all', 
    status_code=status.HTTP_200_OK,
    response_model=GetAllTrainingSessionsResponse
)
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    sessions = await training_session.get_many(db, user_id=user.id)
    return GetAllTrainingSessionsResponse(sessions=sessions)

@router.post('/', 
    status_code=status.HTTP_201_CREATED,
    response_model=TrainingSessionCreateResponse
)
async def create_session(
    request: TrainingSessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        session = await create_training_session(
            db=db,
            user_id=user.id,
            question_type=request.question_type,
            min_frequency=request.min_frequency,
            max_frequency=request.max_frequency,
            gain_level=request.gain_level
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e