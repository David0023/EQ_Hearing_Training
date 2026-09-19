from fastapi import APIRouter, Depends, HTTPException, status
from fastapi. security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.frequency import FrequencyGroupResponse, FrequencyGroupItem
from core.dependencies import get_db, get_current_user
from models.user import User
from domain.training.frequencies import FREQUENCY_GROUPS


router = APIRouter(
    prefix='/frequency',
    tags=['frequency']
)

@router.get('/groups', response_model=FrequencyGroupResponse, status_code=status.HTTP_200_OK)
async def get_frequency_list():
    return FrequencyGroupResponse(
        available_groups=[
            FrequencyGroupItem(
                name=group,
                frequencies=list(frequencies),
            )
            for group, frequencies in FREQUENCY_GROUPS.items()
        ]
    )