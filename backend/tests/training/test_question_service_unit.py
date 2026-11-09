from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from training.enums import QuestionType, SessionStatus
from training.question import service
from training.session import service as session_service
import db.models  # noqa: F401


def _session():
    return SimpleNamespace(
        id=3,
        num_questions=2,
        session_status=SessionStatus.IN_PROGRESS,
        config={"question_plan": [{"question_type": "simple_blind", "count": 2, "settings": {
            "min_frequency": 125, "max_frequency": 250, "min_gain": 3, "max_gain": 4.5,
        }}]},
    )


def test_question_plan_lookup_and_completed_plan():
    session = _session()
    question = SimpleNamespace(sequence=2, question_type=QuestionType.SIMPLE_BLIND)
    assert service.get_question_answer_options(session, question)["frequencies"] == [125, 250]
    assert service._get_next_plan_block(session, 1)["count"] == 2
    with pytest.raises(service.SessionCompletedException):
        service._get_next_plan_block(session, 2)
    session.config["question_plan"] = None
    with pytest.raises(ValueError, match="must be a list"):
        service._get_next_plan_block(session, 0)


@pytest.mark.anyio
async def test_create_question_persists_generated_question(monkeypatch):
    session = _session()
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    monkeypatch.setattr(service.repository, "get_all", AsyncMock(return_value=[]))
    created = None
    async def create(db, question, flush=False):
        nonlocal created
        question.id = 10
        created = question
        return question
    monkeypatch.setattr(service.repository, "create", create)
    async def get_one(db, question_type, *conditions, **kwargs):
        return created
    monkeypatch.setattr(service.repository, "get_one", get_one)
    question = await service.create_question(db, session)
    assert question.id == 10
    assert question.sequence == 1
    assert question.simple_blind.target_frequency in (125, 250)
    db.commit.assert_awaited_once()

    session.session_status = SessionStatus.COMPLETED
    with pytest.raises(service.SessionCompletedException):
        await service.create_question(db, session)


@pytest.mark.anyio
async def test_answer_question_marks_completed_session(monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    session = _session()
    session.num_questions = 1
    question = SimpleNamespace(
        id=10, question_type=QuestionType.GAIN_BLIND, is_answered=False,
    )
    monkeypatch.setattr(service.repository, "get_one", AsyncMock(return_value=question))
    async def record_answer(*args, **kwargs):
        question.is_answered = True
    monkeypatch.setattr(service.repository, "record_answer", AsyncMock(side_effect=record_answer))
    monkeypatch.setattr(service.repository, "get_all", AsyncMock(return_value=[question]))
    monkeypatch.setattr(session_service, "mark_session_complete", AsyncMock())
    monkeypatch.setattr(session_service, "update_timestamp", AsyncMock())
    strategy = SimpleNamespace(record_answer=AsyncMock(return_value=True))
    monkeypatch.setattr(service, "get_strategy", lambda kind: strategy)
    answer = SimpleNamespace(question_type="gain_blind")
    complete, answered = await service.answer_question(db, session, 10, answer)
    assert complete and answered is question
    session_service.mark_session_complete.assert_awaited_once_with(db, session)
    db.commit.assert_awaited_once()

    question.is_answered = True
    with pytest.raises(service.QuestionAnswerException, match="already answered"):
        await service.answer_question(db, session, 10, answer)
