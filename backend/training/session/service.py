from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from training.enums import QuestionType, SessionStatus
from training.session.model import TrainingSession
from training.session import repository
from training.question.types.registry import get_strategy

from training.session.schema import (
    SessionCreateRequest,
    SessionSummary,
)
from training.question import repository as question_repository

class SessionCreationException(Exception):
    pass

class SessionDeletionException(Exception):
    pass

class PaginationException(Exception):
    pass

async def get_my_sessions(
    db: AsyncSession, user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> list[TrainingSession]:
    if page <= 0:
        raise PaginationException("Page number must be positive")
    if page_size <= 0:
            raise PaginationException("Page size must be positive")
    return await repository.get_many(
        db, TrainingSession.user_id==user_id,
        skip=(page-1)*page_size,
        limit=page_size,
        order_by=(
            TrainingSession.last_accessed_at.desc(),
            TrainingSession.id.desc(),
        ),
    )

async def summarize_sessions(
    db: AsyncSession,
    sessions: list[TrainingSession]
) -> list[SessionSummary]:
    stats_by_session = await question_repository.get_session_statistics(
        db, [session.id for session in sessions]
    )

    summaries: list[SessionSummary] = []
    for session in sessions:
        answered, correct = stats_by_session.get(session.id, (0, 0))
        summaries.append(
            SessionSummary(
                session=session,
                answered_count=answered,
                correct_count=correct,
                accuracy=round(correct / answered * 100) if answered else 0,
            )
        )
    return summaries

async def get_my_session_summaries(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> list[SessionSummary]:
    """Return a page of a user's sessions with aggregated question statistics."""
    sessions = await get_my_sessions(db, user_id, page=page, page_size=page_size)
    return await summarize_sessions(db, sessions)

async def get_session(
    db: AsyncSession, *,
    session_id: int, lock: bool=False, load_questions: bool=False
) -> TrainingSession | None:
    return await repository.get_one(
        db, TrainingSession.id==session_id, 
        lock=lock, load_questions=load_questions
    )


async def create_session(
    db: AsyncSession,
    user_id: int,
    request: SessionCreateRequest,
) -> TrainingSession:
    """Validate training settings and create a training session.

    Raises:
        SessionCreationException: If a frequency or gain setting is invalid.
    """

    setting = request.setting
    try:
        strategy = get_strategy(QuestionType(setting.question_type))
        plan_item = strategy.build_plan_item(
            count=request.num_questions,
            settings=setting.model_dump(exclude={"question_type"}),
        )
    except ValueError as exc:
        raise SessionCreationException(str(exc)) from exc

    session = TrainingSession(
        user_id=user_id,
        num_questions=request.num_questions,
        config={"question_plan": [plan_item]},
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

async def update_timestamp(db: AsyncSession, session: TrainingSession):
    """Update session accessed time. No commit"""
    session = await repository.update(
            db, session, flush=True,
            last_accessed_at=datetime.now(timezone.utc)
        )
    return session


async def session_result(
    db: AsyncSession,
    sessions: TrainingSession
):
    """TODO"""
