from fastapi import APIRouter

from api.v1.training.question import router as question_router
from api.v1.training.session import router as session_router

router = APIRouter(
    prefix='/training',
    tags=['training']
)

router.include_router(question_router)
router.include_router(session_router)
