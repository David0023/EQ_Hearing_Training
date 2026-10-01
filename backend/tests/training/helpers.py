BASE = '/api/v1/training'
SETTINGS = {
    'num_questions': 2,
    'question_type': 'simple_blind',
    'min_frequency': 125,
    'max_frequency': 1000,
    'gain_level': 3.0,
}


async def create_session(client, headers, settings=None):
    response = await client.post(
        f'{BASE}/sessions', headers=headers, json=settings or SETTINGS,
    )
    assert response.status_code == 201, response.text
    return response.json()['id']
