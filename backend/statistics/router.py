from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.database import get_db
from user.model import User
from training.session import repository as session_repository
from training.question import repository as quesiton_repository


router = APIRouter(
    prefix='/statistics',
    tags=['statistics']
)

@router.get('/training/session/{session_id}')
async def my_statistics(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ...
    # TODO: Finish this

@router.get('/me')
async def my_statistics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ...
    # TODO: Finish this
