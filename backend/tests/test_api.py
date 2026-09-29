import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from db import database
from training.session import repository as session_repository
from user import repository as user_repository

pytestmark = pytest.mark.anyio
BASE = '/api/vi/training'
SETTINGS = {
    'num_questions': 2,
    'question_type': 'simple_blind', 'min_frequency': 125,
    'max_frequency': 1000, 'gain_level': 3.0,
}


async def create_session(client, headers):
    response = await client.post(f'{BASE}/session/', headers=headers, json=SETTINGS)
    assert response.status_code == 201, response.text
    return response.json()['id']


async def test_routes_and_metadata(client):
    response = await client.get('/openapi.json')
    assert response.status_code == 200
    paths = response.json()['paths']
    assert set(paths) == {
        '/', '/auth/register', '/auth/login', '/auth/me',
        f'{BASE}/session/all', f'{BASE}/session/', f'{BASE}/session/{{session_id}}',
        f'{BASE}/question/all/{{session_id}}', f'{BASE}/question/{{session_id}}',
        f'{BASE}/question/{{session_id}}/{{question_id}}',
        '/api/vi/info/frequency/groups', '/api/vi/info/gain/options',
    }
    assert (await client.get('/api/vi/info/frequency/groups')).json()['available_groups']
    assert 3.0 in (await client.get('/api/vi/info/gain/options')).json()['gain_options']
    # DB initialization must register models even without importing any routers.
    result = subprocess.run([
        sys.executable, '-c',
        'from db.database import Base; from sqlalchemy.orm import configure_mappers; '
        'configure_mappers(); '
        'assert set(Base.metadata.tables) == {"users", "training_sessions", "training_questions"}',
    ], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


async def test_auth_and_account_deletion(client, headers):
    assert (await client.get('/auth/me')).status_code == 401
    response = await client.get('/auth/me', headers=headers)
    assert response.json()['email'] == 'tester@example.com'
    assert 'hashed_pwd' not in response.json()
    response = await client.post('/auth/login', data={
        'username': 'tester@example.com', 'password': 'wrong',
    })
    assert response.status_code == 401
    duplicate = await client.post('/auth/register', json={
        'username': 'tester', 'email': 'tester@example.com', 'password': 'test-password',
    })
    assert duplicate.status_code == 400
    sid = await create_session(client, headers)
    assert (await client.post(f'{BASE}/question/{sid}', headers=headers)).status_code == 201
    response = await client.delete('/auth/me', headers=headers)
    assert response.status_code == 204 and not response.content
    assert (await client.get('/auth/me', headers=headers)).status_code == 401
    async with database.SessionLocal() as db:
        assert await session_repository.get_many(db) == []


async def test_question_lifecycle_and_session_serialization(client, headers, monkeypatch):
    get_one = AsyncMock(wraps=session_repository.get_one)
    monkeypatch.setattr(session_repository, 'get_one', get_one)
    sid = await create_session(client, headers)
    response = await client.post(f'{BASE}/question/{sid}', headers=headers)
    assert response.status_code == 201, response.text
    question = response.json()['question']
    assert get_one.call_args.kwargs['lock'] is True
    resumed = await client.post(f'{BASE}/question/{sid}', headers=headers)
    assert resumed.status_code == 200
    assert resumed.json()['question']['id'] == question['id']
    payload = {'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']}
    url = f'{BASE}/question/{sid}/{question["id"]}'
    answer = await client.put(url, headers=headers, json=payload)
    assert answer.status_code == 200, answer.text
    assert answer.json()['is_correct'] is True
    assert answer.json()['answered_at'] is not None
    assert get_one.call_args.kwargs['lock'] is True
    assert (await client.put(url, headers=headers, json=payload)).status_code == 400
    next_question = await client.post(f'{BASE}/question/{sid}', headers=headers)
    assert next_question.status_code == 201
    assert next_question.json()['question']['id'] != question['id']
    detail = await client.get(f'{BASE}/session/{sid}', headers=headers)
    assert detail.status_code == 200, detail.text
    assert len(detail.json()['training_questions']) == 2
    listing = await client.get(f'{BASE}/question/all/{sid}', headers=headers)
    assert listing.status_code == 200 and len(listing.json()['questions']) == 2
    sessions = await client.get(f'{BASE}/session/all', headers=headers)
    assert len(sessions.json()['sessions']) == 1
    assert (await client.delete(f'{BASE}/session/{sid}', headers=headers)).status_code == 204
    assert (await client.get(f'{BASE}/session/{sid}', headers=headers)).status_code == 404
    from db.database import SessionLocal
    from training.question import repository as question_repository
    async with SessionLocal() as db:
        assert await question_repository.get_many(db) == []


async def test_session_access_controls(client, headers):
    sid = await create_session(client, headers)
    question = (await client.post(f'{BASE}/question/{sid}', headers=headers)).json()['question']
    await client.post('/auth/register', json={
        'username': 'other', 'email': 'other@example.com', 'password': 'test-password',
    })
    token = (await client.post('/auth/login', data={
        'username': 'other@example.com', 'password': 'test-password',
    })).json()['access_token']
    other = {'Authorization': f'Bearer {token}'}
    for session_id, expected in [(sid, 403), (99999, 404)]:
        for method, path, body in [
            ('GET', f'/session/{session_id}', None),
            ('DELETE', f'/session/{session_id}', None),
            ('GET', f'/question/all/{session_id}', None),
            ('POST', f'/question/{session_id}', None),
            ('PUT', f'/question/{session_id}/{question["id"]}', {'user_frequency': 125, 'user_gain': 3}),
        ]:
            response = await client.request(method, BASE + path, headers=other, json=body)
            assert response.status_code == expected, response.text


@pytest.mark.parametrize('override', [
    {'min_frequency': 123}, {'gain_level': 2},
    {'min_frequency': 1000, 'max_frequency': 125},
])
async def test_invalid_session_settings(client, headers, override):
    response = await client.post(f'{BASE}/session/', headers=headers, json=SETTINGS | override)
    assert response.status_code == 400, response.text


async def test_question_must_belong_to_session(client, headers):
    first = await create_session(client, headers)
    second = await create_session(client, headers)
    question = (await client.post(f'{BASE}/question/{first}', headers=headers)).json()['question']
    response = await client.put(f'{BASE}/question/{second}/{question["id"]}', headers=headers,
                                json={'user_frequency': 125, 'user_gain': 3})
    assert response.status_code == 404


async def test_user_creation_failure_rolls_back(client, headers):
    from db.database import SessionLocal
    async with SessionLocal() as db:
        with pytest.raises(user_repository.UserCreationException):
            await user_repository.create(db, 'tester@example.com', 'duplicate', 'hash')
        # The same session must be usable after the failed commit.
        created = await user_repository.create(db, 'fresh@example.com', 'fresh', 'hash')
        assert created.id is not None


async def test_last_answer_completes_session(client, headers):
    response = await client.post(
        f'{BASE}/session/', headers=headers, json=SETTINGS | {'num_questions': 1},
    )
    assert response.status_code == 201, response.text
    sid = response.json()['id']
    question = (await client.post(f'{BASE}/question/{sid}', headers=headers)).json()['question']
    response = await client.put(
        f'{BASE}/question/{sid}/{question["id"]}', headers=headers,
        json={'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']},
    )
    assert response.status_code == 200, response.text
    detail = (await client.get(f'{BASE}/session/{sid}', headers=headers)).json()
    assert detail['session_status'] == 'completed'
    assert detail['completed_at'] is not None
    assert detail['training_questions'][0]['is_answered'] is True
    response = await client.post(f'{BASE}/question/{sid}', headers=headers)
    assert response.status_code == 400, response.text


async def test_completion_failure_rolls_back_answer(client, headers, monkeypatch):
    from training.session import service as session_service

    response = await client.post(
        f'{BASE}/session/', headers=headers, json=SETTINGS | {'num_questions': 1},
    )
    sid = response.json()['id']
    question = (await client.post(f'{BASE}/question/{sid}', headers=headers)).json()['question']
    monkeypatch.setattr(session_service, 'mark_session_complete', AsyncMock(side_effect=RuntimeError('completion failed')))
    with pytest.raises(RuntimeError, match='completion failed'):
        await client.put(
            f'{BASE}/question/{sid}/{question["id"]}', headers=headers,
            json={'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']},
        )
    detail = (await client.get(f'{BASE}/session/{sid}', headers=headers)).json()
    assert detail['session_status'] == 'in_progress'
    assert detail['completed_at'] is None
    assert detail['training_questions'][0]['is_answered'] is False


@pytest.mark.parametrize('method', ['delete_one', 'delete_many'])
async def test_question_deletion_preserves_other_rows(client, headers, method):
    from training.question import repository as question_repository
    from training.question.model import TrainingQuestion

    first = await create_session(client, headers)
    second = await create_session(client, headers)
    keep = (await client.post(f'{BASE}/question/{first}', headers=headers)).json()['question']['id']
    target = (await client.post(f'{BASE}/question/{second}', headers=headers)).json()['question']['id']
    async with database.SessionLocal() as db:
        deleted = await getattr(question_repository, method)(
            db, TrainingQuestion.id == target, flush=True,
        )
        assert deleted == 1
        assert [q.id for q in await question_repository.get_many(db)] == [keep]
        await db.rollback()
    async with database.SessionLocal() as db:
        assert [q.id for q in await question_repository.get_many(db)] == [keep, target]
        await getattr(question_repository, method)(db, TrainingQuestion.id == target)
        await db.commit()
    async with database.SessionLocal() as db:
        assert [q.id for q in await question_repository.get_many(db)] == [keep]
