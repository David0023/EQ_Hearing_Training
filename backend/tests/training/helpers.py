from httpx import AsyncClient, Response
from collections.abc import AsyncGenerator

BASE = '/api/v1/training'
def format_simple_blind_settings(
    min_frequency: float = 125,
    max_frequency: float = 1000,
    min_gain: float = 3.0,
    max_gain: float = 3.0,
) -> dict:
    return {
        'question_type': 'simple_blind',
        'min_frequency': min_frequency,
        'max_frequency': max_frequency,
        'min_gain': min_gain,
        'max_gain': max_gain,
    }


def format_gain_blind_settings(
    min_frequency: float = 125,
    max_frequency: float = 1000,
) -> dict:
    return {
        'question_type': 'gain_blind',
        'min_frequency': min_frequency,
        'max_frequency': max_frequency,
    }

def format_session_settings(
    num_questions: int = 2,
    setting: dict = format_simple_blind_settings()
) -> dict:
    return {'num_questions': num_questions, 'setting': setting}

async def create_session(
    client: AsyncGenerator[AsyncClient, None],
    settings: dict = format_session_settings()
) -> Response:
    return await client.post(
        f'{BASE}/sessions', json=settings,
    )
