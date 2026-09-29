from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from training.session.schema import (
    TrainingSessionCreateRequest,
    TrainingSessionCreateResponse,
    GetTrainingSessionWithQuestionsResponse,
    GetAllTrainingSessionsResponse
)

from training.session.service import create_training_session, SessionCreationException
from auth.dependencies import get_current_user
from db.database import get_db
from user.model import User
from training.session.model import TrainingSession
from training.session import repository
from training.dependencies import get_session_with_questions, get_locked_session

router = APIRouter(
    prefix='/session',
    tags=['session']
)

@router.get('/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllTrainingSessionsResponse
)
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Return all training sessions belonging to the authenticated user."""
    sessions = await repository.get_many(db, User.id==user.id)
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
        return await create_training_session(
            db=db,
            user_id=user.id,
            request=request
        )
    except SessionCreationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

@router.get('/{session_id}',
    status_code=status.HTTP_200_OK,
    response_model=GetTrainingSessionWithQuestionsResponse
)
async def get_single_session(
    session: TrainingSession = Depends(get_session_with_questions),
):
    return session


@router.delete('/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_session(
    db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    await repository.delete_this(db, session)
