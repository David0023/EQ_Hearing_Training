from httpx import AsyncClient, Resposne
from collections.abc import AsyncGenerator
from pathlib import Path

BASE = '/api/v1/training'
SETTINGS = {
    'num_questions': 2,
    'setting': {
        'question_type': 'simple_blind',
        'min_frequency': 125,
        'max_frequency': 1000,
        'min_gain': 3.0,
        'max_gain': 3.0,
    },
}


async def create_session(
    client: AsyncGenerator[AsyncClient, None],
    settings: dict | None = SETTINGS
) -> Resposne:
    return await client.post(
        f'{BASE}/sessions', json=settings,
    )