import pytest
from collections.abc import AsyncGenerator
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

from tests.training.helpers import (
    create_session,
    format_session_settings,
    format_gain_blind_settings,
    format_simple_blind_settings,
    BASE
)

async def test_session_creation_success(authenticated_client: AsyncGenerator[AsyncClient, None]):
    setting = format_session_settings(
        2, format_simple_blind_settings()
    )
    response = await create_session(authenticated_client, setting)
    assert response.status_code == 201

    setting = format_session_settings(
        2, format_gain_blind_settings()
    )
    response = await create_session(authenticated_client, setting)
    assert response.status_code == 201


# Test session creation with invalid frequency or gain settings
# Test session 
