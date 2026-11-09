from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from training.enums import QuestionType, SessionStatus
from training.session import service
from training.session.schema import SessionCreateRequest


def _request(question_type="simple_blind"):
    if question_type == "gain_blind":
        setting = {"question_type": question_type, "min_frequency": 125, "max_frequency": 500}
    else:
        setting = {
            "question_type": question_type,
            "min_frequency": 125, "max_frequency": 500,
            "min_gain": 3, "max_gain": 6,
        }
    return SessionCreateRequest(num_questions=3, setting=setting)


@pytest.mark.anyio
async def test_session_pagination_and_summaries(monkeypatch):
    db = object()
    now = datetime.now(timezone.utc)
    sessions = [SimpleNamespace(
        id=index, num_questions=3, config={}, session_status=SessionStatus.IN_PROGRESS,
        started_at=now, last_accessed_at=now, completed_at=None,
    ) for index in (1, 2)]
    monkeypatch.setattr(service.repository, "get_many", AsyncMock(return_value=sessions))
    with pytest.raises(service.PaginationException):
        await service.get_my_sessions(db, 7, page=0)
    with pytest.raises(service.PaginationException):
        await service.get_my_sessions(db, 7, page_size=0)
    assert await service.get_my_sessions(db, 7) == sessions

    monkeypatch.setattr(service.question_repository, "get_session_statistics", AsyncMock(return_value={1: (4, 3)}))
    summaries = await service.summarize_sessions(db, sessions)
    assert [summary.accuracy for summary in summaries] == [75, 0]
    assert await service.get_my_session_summaries(db, 7) == summaries


@pytest.mark.anyio
async def test_session_creation_validates_and_persists(monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock(), refresh=AsyncMock())
    async def create(db, session, flush=False):
        session.id = 4
        return session
    monkeypatch.setattr(service.repository, "create", create)
    session = await service.create_session(db, 9, _request())
    assert session.id == 4
    db.commit.assert_awaited_once()
    assert session.config["question_plan"][0]["question_type"] == QuestionType.SIMPLE_BLIND.value

    invalid_request = _request()
    invalid_request.setting.min_gain = 6
    invalid_request.setting.max_gain = 3
    with pytest.raises(service.SessionCreationException):
        await service.create_session(db, 9, invalid_request)


@pytest.mark.anyio
async def test_session_delete_updates_and_result(monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    session = SimpleNamespace()
    monkeypatch.setattr(service.repository, "delete_this", AsyncMock())
    await service.delete_session(db, session)
    db.commit.assert_awaited_once()

    monkeypatch.setattr(service.repository, "update", AsyncMock(return_value=session))
    assert await service.mark_session_complete(db, session) is session
    assert await service.update_timestamp(db, session) is session
    assert await service.session_result(db, session) is None
