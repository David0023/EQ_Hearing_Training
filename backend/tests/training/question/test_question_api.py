from unittest.mock import AsyncMock

import pytest

from training.session import repository as session_repository
from tests.training.helpers import BASE, create_session

pytestmark = pytest.mark.anyio


async def test_question_lifecycle_and_session_serialization(client, headers, monkeypatch):
    get_one = AsyncMock(wraps=session_repository.get_one)
    monkeypatch.setattr(session_repository, 'get_one', get_one)
    sid = await create_session(client, headers)
    response = await client.post(f'{BASE}/sessions/{sid}/questions', headers=headers)
    assert response.status_code == 201, response.text
    question = response.json()['question']
    assert get_one.call_args.kwargs['lock'] is True
    resumed = await client.post(f'{BASE}/sessions/{sid}/questions', headers=headers)
    assert resumed.status_code == 200
    assert resumed.json()['question']['id'] == question['id']
    payload = {'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']}
    url = f'{BASE}/sessions/{sid}/questions/{question["id"]}'
    answer = await client.put(url, headers=headers, json=payload)
    assert answer.status_code == 200, answer.text
    assert answer.json()['is_correct'] is True
    assert answer.json()['answered_at'] is not None
    assert get_one.call_args.kwargs['lock'] is True
    assert (await client.put(url, headers=headers, json=payload)).status_code == 400
    next_question = await client.post(f'{BASE}/sessions/{sid}/questions', headers=headers)
    assert next_question.status_code == 201
    assert next_question.json()['question']['id'] != question['id']
    detail = await client.get(f'{BASE}/sessions/{sid}', headers=headers)
    assert detail.status_code == 200, detail.text
    assert len(detail.json()['training_questions']) == 2
    listing = await client.get(f'{BASE}/sessions/{sid}/questions', headers=headers)
    assert listing.status_code == 200 and len(listing.json()['questions']) == 2
    sessions = await client.get(f'{BASE}/sessions/recent', headers=headers)
    assert len(sessions.json()['sessions']) == 1
    assert (await client.delete(f'{BASE}/sessions/{sid}', headers=headers)).status_code == 204
    assert (await client.get(f'{BASE}/sessions/{sid}', headers=headers)).status_code == 404
    from db.database import SessionLocal
    from training.question import repository as question_repository
    async with SessionLocal() as db:
        assert await question_repository.get_all(db) == []

async def test_question_must_belong_to_session(client, headers):
    first = await create_session(client, headers)
    second = await create_session(client, headers)
    question = (await client.post(f'{BASE}/sessions/{first}/questions', headers=headers)).json()['question']
    response = await client.put(f'{BASE}/sessions/{second}/questions/{question["id"]}', headers=headers,
                                json={'user_frequency': 125, 'user_gain': 3})
    assert response.status_code == 404
