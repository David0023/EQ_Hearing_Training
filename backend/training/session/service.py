from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from training.enums import SessionStatus
from training.session.model import TrainingSession
from training.session import repository
from training.domain.info import validate_frequency, validate_gain

from training.session.schema import TrainingSessionCreateRequest

class SessionCreationException(Exception):
    pass

class SessionDeletionException(Exception):
    pass

async def get_all_my_sessions(db: AsyncSession, user_id: int) -> list[TrainingSession]:
    return await repository.get_many(db, TrainingSession.user_id==user_id)

async def get_session(
    db: AsyncSession, *,
    session_id: int, lock: bool=False, load_questions: bool=False
) -> TrainingSession | None:
    return await repository.get_one(
        db, TrainingSession.id==session_id, 
        lock=lock, load_questions=load_questions
    )


async def create_training_session(
    db: AsyncSession,
    user_id: int,
    request: TrainingSessionCreateRequest,
) -> TrainingSession:
    """Validate training settings and create a training session.

    Raises:
        SessionCreationException: If a frequency or gain setting is invalid.
    """

    if not (validate_frequency(request.min_frequency) and validate_frequency(request.max_frequency)):
        raise SessionCreationException("Invalid Frequency Option")
    if request.min_frequency > request.max_frequency:
        raise SessionCreationException("Invalid Frequency Range")
    if not validate_gain(request.gain_level):
        raise SessionCreationException("Invalid Gain Level")
    session = TrainingSession(
        user_id=user_id,
        num_questions=request.num_questions,
        question_type=request.question_type,
        min_frequency=request.min_frequency,
        max_frequency=request.max_frequency,
        gain_level=request.gain_level
    )

    try:
        session = await repository.create(db, session, flush=True)
        await db.commit()
        await db.refresh(session)
        return session
    except Exception:
        await db.rollback()
        raise

async def delete_session(
    db: AsyncSession,
    session: TrainingSession
) -> None:
    try:
        await repository.delete_this(db=db, session=session)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise SessionDeletionException("Training session cannot be deleted") from e

async def mark_session_complete(
    db: AsyncSession,
    session: TrainingSession,
) -> TrainingSession:
    """
    Mark given session as complete. No commit.
    """
    session = await repository.update(
        db, session, flush=True,
        session_status=SessionStatus.COMPLETED, completed_at=datetime.now(timezone.utc)
    )
    return session
