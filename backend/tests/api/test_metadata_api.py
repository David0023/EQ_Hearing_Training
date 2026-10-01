import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.anyio


async def test_routes_and_metadata(client):
    response = await client.get('/openapi.json')
    assert response.status_code == 200
    paths = response.json()['paths']

    expected_paths = {
        '/',
        '/auth/register',
        '/auth/login',
        '/api/v1/users/me',
        '/api/v1/training/sessions/recent',
        '/api/v1/training/sessions',
        '/api/v1/training/sessions/{session_id}',
        '/api/v1/training/sessions/{session_id}/questions',
        '/api/v1/training/sessions/{session_id}/questions/{question_id}',
        '/api/v1/training/infos/frequency/groups',
        '/api/v1/training/infos/gain/options',
        '/api/v1/statistics/today',
        '/api/v1/statistics/week',
    }
    assert set(paths) == expected_paths
    assert set(paths['/api/v1/training/sessions/{session_id}/questions']) == {'get', 'post'}
    assert set(paths['/api/v1/training/sessions/{session_id}/questions/{question_id}']) == {'put'}
    assert (await client.get('/api/v1/training/infos/frequency/groups')).json()['available_groups']
    assert 3.0 in (await client.get('/api/v1/training/infos/gain/options')).json()['gain_options']

    # DB initialization must register models even without importing any routers.
    result = subprocess.run([
        sys.executable, '-c',
        'from db.database import Base; from sqlalchemy.orm import configure_mappers; '
        'configure_mappers(); '
        'assert set(Base.metadata.tables) == {"users", "training_sessions", "training_questions"}',
    ], cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
