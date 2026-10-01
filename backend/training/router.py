from fastapi import APIRouter

from training.question.router import router as question_router
from training.session.router import router as session_router
from training.info.router import router as info_router

router = APIRouter(
    prefix='/training',
    tags=['training']
)

router.include_router(question_router)
router.include_router(session_router)
router.include_router(info_router)
