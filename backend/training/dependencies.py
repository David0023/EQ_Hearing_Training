from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_current_user
from db.database import get_db
from training.session import repository
from training.session.model import TrainingSession
from user.model import User


def authorize_session(user: User, session: TrainingSession | None) -> TrainingSession:
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Non-existing training session")
    if session.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not accessible")
    return session


async def get_session_with_questions(
    session_id: int, db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrainingSession:
    session = await repository.get_one_with_questions(db, id=session_id)
    return authorize_session(user, session)


async def get_locked_session(
    session_id: int, db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrainingSession:
    session = await repository.get_one(db, TrainingSession.id == session_id, lock=True)
    return authorize_session(user, session)
