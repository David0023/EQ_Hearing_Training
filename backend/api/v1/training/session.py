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
from models.training_session import TrainingSession
from repositories import training_session, training_question

router = APIRouter(
    prefix='/session',
    tags=['session']
)

async def _authorize_session(user: User, session: TrainingSession | None):
    """
    Check if the session exists and if it belongs to the user.
    Raises:
        HTTPException: 404 if non-existent, 403 if not accessible.
    """
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")

    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")
    
##---------------------------------------
@router.get('/all', 
    status_code=status.HTTP_200_OK,
    response_model=GetAllTrainingSessionsResponse
)
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Return all training sessions belonging to the authenticated user."""
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
    """Create and return a training session for the authenticated user.

    Raises:
        HTTPException: If session creation fails.
    """
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

@router.get('/{session_id}', 
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingSessionWithQuestionsResponse
)
async def get_single_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Return one accessible training session with its questions.

    Raises:
        HTTPException: If the session does not exist or is not accessible.
    """
    session = await training_session.get_one_with_questions(db, id=session_id)

    _authorize_session(user, session)

    return session

@router.delete(
    '/{session_id}', 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_one_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a session with given ID for the authenticated user.
    
        Raises:
            HTTPException: If session delete fails
        """
    session = await training_session.get_one(db, TrainingSession.id==session_id)
    
    _authorize_session(user, session)

    await training_session.delete_one(db, TrainingSession.id==session_id)

    # SQL will run deletion of question.