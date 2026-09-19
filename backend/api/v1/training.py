from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.training_session import (
    TrainingSessionCreateRequest, 
    TrainingSessionCreateResponse,
    GetTrainingSessionWithAttemptsResponse,
    GetAllTrainingSessionsResponse
)
from schemas.training_attempt import GetTrainingAttmptResponse

from services.training import create_training_session, create_training_question
from core.dependencies import get_db, get_current_user
from models.user import User
from models.training_session import TrainingSession
from models.training_attempt import TrainingAttempt
from repositories.training_session import (
    get_one_training_session, get_training_sessions, get_one_training_session_with_attempts
)
from repositories.training_attempt import get_one_training_attempt

router = APIRouter(
    prefix='/training',
    tags=['training']
)

def _validate_training_session(
    training_session: TrainingSession | None,
    user_id: User = Depends(get_current_user)
) -> TrainingSession:
    if not training_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")
    if training_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")
    return training_session


##---------------------------------------
@router.get('/session/{session_id}', 
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingSessionWithAttemptsResponse
)
async def get_single_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return _validate_training_session(
        training_session= await get_one_training_session_with_attempts(db, id=session_id),
        user_id=user.id
    )

@router.get('/sessions', 
    status_code=status.HTTP_200_OK,
    response_model=GetAllTrainingSessionsResponse
)
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    training_sessions = await get_training_sessions(db, user_id=user.id)
    return GetAllTrainingSessionsResponse(sessions=training_sessions)

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

@router.post('/session/{session_id}/question', 
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingAttmptResponse
)
async def get_question_or_create(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    t_session = _validate_training_session(
            training_session= await get_one_training_session(db, id=session_id),
            user_id=user.id
    )

    unanswered_attempt = await get_one_training_attempt(
        db,
        training_session_id=t_session.id,
        is_answered=False
    )
    if unanswered_attempt:
        return GetTrainingAttmptResponse(
            attempt=unanswered_attempt,
            question_type=t_session.question_type
        )

    return GetTrainingAttmptResponse(
        attempt= await create_training_question(db, t_session),
        question_type=t_session.question_type
    )
    


