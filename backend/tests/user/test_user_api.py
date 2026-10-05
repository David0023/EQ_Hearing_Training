from unittest.mock import AsyncMock

import pytest

from tests.training.helpers import BASE, SETTINGS, create_session

pytestmark = pytest.mark.anyio

async def test_user_creation():
    ...