from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_current_user
from db.database import get_db
from user import service
from user.model import User
from user.schema import UserMeResponse, UserSelfAuthenticationRequest

# Keep the existing public URLs while separating account routes from authentication.
router = APIRouter(prefix="/users", tags=["user"])

@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserMeResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Return the authenticated user."""
    return current_user

@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    request: UserSelfAuthenticationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the authenticated user."""
    try:
        await service.delete_this(request, db, current_user)
    except service.DeleteUserException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
