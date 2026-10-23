from unittest.mock import AsyncMock

import pytest

from tests.training.helpers import BASE, SETTINGS, create_session

pytestmark = pytest.mark.anyio


async def test_recent_sessions_pagination(client, headers):
    session_ids = [await create_session(client, headers) for _ in range(3)]

    first_page = await client.get(
        f'{BASE}/sessions/recent?page=1&page_size=2', headers=headers,
    )
    second_page = await client.get(
        f'{BASE}/sessions/recent?page=2&page_size=2', headers=headers,
    )

    assert first_page.status_code == 200, first_page.text
    assert second_page.status_code == 200, second_page.text
    first_ids = [item['session']['id'] for item in first_page.json()['sessions']]
    second_ids = [item['session']['id'] for item in second_page.json()['sessions']]
    assert len(first_ids) == 2
    assert len(second_ids) == 1
    assert set(first_ids + second_ids) == set(session_ids)

async def test_session_access_controls(client, headers):
    sid = await create_session(client, headers)
    question = (await client.post(f'{BASE}/sessions/{sid}/questions/resume', headers=headers)).json()['question']
    await client.post('/auth/register', json={
        'username': 'other', 'email': 'other@example.com', 'password': 'test-password',
    })
    token = (await client.post('/auth/login', data={
        'username': 'other@example.com', 'password': 'test-password',
    })).json()['access_token']
    other = {'Authorization': f'Bearer {token}'}
    for session_id, expected in [(sid, 403), (99999, 404)]:
        for method, path, body in [
            ('GET', f'/sessions/{session_id}', None),
            ('DELETE', f'/sessions/{session_id}', None),
            ('GET', f'/sessions/{session_id}/questions', None),
            ('POST', f'/sessions/{session_id}/questions/resume', None),
            ('PUT', f'/sessions/{session_id}/questions/{question["id"]}', {'user_frequency': 125, 'user_gain': 3}),
        ]:
            response = await client.request(method, BASE + path, headers=other, json=body)
            assert response.status_code == expected, response.text

@pytest.mark.parametrize('override', [
    {'min_frequency': 123}, {'min_gain': 2},
    {'min_frequency': 1000, 'max_frequency': 125},
    {'min_gain': 9, 'max_gain': 3},
])
async def test_invalid_session_settings(client, headers, override):
    response = await client.post(f'{BASE}/sessions', headers=headers, json=SETTINGS | override)
    assert response.status_code == 400, response.text

async def test_last_answer_completes_session(client, headers):
    response = await client.post(
        f'{BASE}/sessions', headers=headers, json=SETTINGS | {'num_questions': 1},
    )
    assert response.status_code == 201, response.text
    sid = response.json()['id']
    question = (await client.post(f'{BASE}/sessions/{sid}/questions/resume', headers=headers)).json()['question']
    response = await client.put(
        f'{BASE}/sessions/{sid}/questions/{question["id"]}', headers=headers,
        json={'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']},
    )
    assert response.status_code == 200, response.text
    detail = (await client.get(f'{BASE}/sessions/{sid}', headers=headers)).json()
    assert detail['session_status'] == 'completed'
    assert detail['completed_at'] is not None
    assert detail['training_questions'][0]['is_answered'] is True
    assert detail['training_questions'][0]['question_type'] == 'simple_blind'
    assert detail['training_questions'][0]['target_frequency'] > 0
    response = await client.post(f'{BASE}/sessions/{sid}/questions/resume', headers=headers)
    assert response.status_code == 400, response.text

async def test_completion_failure_rolls_back_answer(client, headers, monkeypatch):
    from training.session import service as session_service

    response = await client.post(
        f'{BASE}/sessions', headers=headers, json=SETTINGS | {'num_questions': 1},
    )
    sid = response.json()['id']
    question = (await client.post(f'{BASE}/sessions/{sid}/questions/resume', headers=headers)).json()['question']
    monkeypatch.setattr(session_service, 'mark_session_complete', AsyncMock(side_effect=RuntimeError('completion failed')))
    with pytest.raises(RuntimeError, match='completion failed'):
        await client.put(
            f'{BASE}/sessions/{sid}/questions/{question["id"]}', headers=headers,
            json={'user_frequency': question['target_frequency'], 'user_gain': question['target_gain']},
        )
    detail = (await client.get(f'{BASE}/sessions/{sid}', headers=headers)).json()
    assert detail['session_status'] == 'in_progress'
    assert detail['completed_at'] is None
    assert detail['training_questions'][0]['is_answered'] is False


async def test_session_persists_question_plan_config(client, headers):
    response = await client.post(f'{BASE}/sessions', headers=headers, json=SETTINGS)
    assert response.status_code == 201, response.text
    assert response.json()['config'] == {
        'question_plan': [{
            'question_type': 'simple_blind',
            'count': SETTINGS['num_questions'],
            'settings': {
                'min_frequency': SETTINGS['min_frequency'],
                'max_frequency': SETTINGS['max_frequency'],
                'min_gain': SETTINGS['min_gain'],
                'max_gain': SETTINGS['max_gain'],
            },
        }],
    }
