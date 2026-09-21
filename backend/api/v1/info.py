from fastapi import APIRouter, status

from schemas.info import (
    FrequencyGroupResponse,
    FrequencyGroupItem,
    GainOptionResponse
)
from domain.training.info import FREQUENCY_GROUPS, STANDARD_GAIN_OPTIONS

router = APIRouter(
    prefix='/info',
    tags=['info']
)

@router.get(
    '/frequency/groups',
    response_model=FrequencyGroupResponse,
    status_code=status.HTTP_200_OK
)
async def get_frequency_list():
    """Return the available frequency groups and their frequencies."""
    return FrequencyGroupResponse(
        available_groups=[
            FrequencyGroupItem(
                name=group,
                frequencies=list(frequencies),
            )
            for group, frequencies in FREQUENCY_GROUPS.items()
        ]
    )

@router.get(
    '/gain/options',
    response_model=GainOptionResponse
)
async def get_gain_options():
    """Return the available gain options."""
    return GainOptionResponse(gain_options=STANDARD_GAIN_OPTIONS)