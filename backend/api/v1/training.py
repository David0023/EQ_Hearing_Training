from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.training_session import (
    TrainingSessionCreateRequest, 
    TrainingSessionCreateResponse,
    GetTrainingSessionResponse
)
from services.training import create_training_session
from core.dependencies import get_db, get_current_user
from models.user import User
from repositories.training_session import get_one_training_session, get_training_sessions


router = APIRouter(
    prefix='/training',
    tags=['training']
)

@router.get('/session/{session_id}', 
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingSessionResponse
)
async def get_single_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    training_session = await get_one_training_session(db, id=session_id)
    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")
    if training_session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")

    return training_session


@router.post('/session', 
    status_code=status.HTTP_201_CREATED,
    response_model=TrainingSessionCreateResponse
)
async def create_session(
    request: TrainingSessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        training_session = await create_training_session(
            db=db,
            user_id=user.id,
            question_type=request.question_type,
            min_frequency=request.min_frequency,
            max_frequency=request.max_frequency,
            gain_level=request.gain_level
        )
        return training_session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e