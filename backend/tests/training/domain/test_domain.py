from httpx import AsyncClient
from collections.abc import AsyncGenerator
import pytest
from tests.training.helpers import BASE

pytestmark = pytest.mark.anyio

async def test_get_frequency_groups(client: AsyncGenerator[AsyncClient, None]):
    from training.domain.info import FREQUENCY_GROUPS
    response = await client.get(f'{BASE}/infos/frequency/groups')

    assert response.status_code == 200
    assert response.json()['available_groups']

    available_groups = {}
    for each in response.json()['available_groups']:
        available_groups[each['name']] = each['frequencies']

    # Must be exactly equal
    for group, f_range in FREQUENCY_GROUPS.items():
        assert available_groups[group]
        assert available_groups[group][0] == f_range[0]
        assert available_groups[group][1] == f_range[1]
        available_groups.pop(group, None)
    assert not available_groups

async def test_get_gain_options(client: AsyncGenerator[AsyncClient, None]):
    from training.domain.info import STANDARD_GAIN_OPTIONS
    response = await client.get(f'{BASE}/infos/gain/options')

    assert response.status_code == 200
    assert response.json()['gain_options']
    assert response.json()['gain_options'] == list(STANDARD_GAIN_OPTIONS)
