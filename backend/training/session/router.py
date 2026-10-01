from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from training.session.schema import (
    TrainingSessionCreateRequest,
    TrainingSessionCreateResponse,
    TrainingSessionWithQuestion,
    TrainingSessionSummaryList,
)

from training.session import service
from auth.dependencies import get_current_user
from db.database import get_db
from user.model import User
from training.session.model import TrainingSession
from training.dependencies import get_session_with_questions, get_locked_session

router = APIRouter(
    prefix='/session',
    tags=['session']
)

@router.get('/recent',
    status_code=status.HTTP_200_OK,
    response_model=TrainingSessionSummaryList
)
async def get_recent_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
):
    """Return given amount of training sessions belonging to the authenticated user."""
    try:
        summaries = await service.get_my_session_summaries(
            db, user.id, page=page, page_size=page_size
        )
        return TrainingSessionSummaryList(sessions=summaries)
    except service.PaginationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

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
        return await service.create_training_session(
            db=db,
            user_id=user.id,
            request=request
        )
    except service.SessionCreationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

@router.get('/{session_id}',
    status_code=status.HTTP_200_OK,
    response_model=TrainingSessionWithQuestion
)
async def get_single_session(session: TrainingSession = Depends(get_session_with_questions)):
    return session


@router.delete('/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_session(
    db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    try:
        await service.delete_session(db, session)
    except service.SessionDeletionException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
