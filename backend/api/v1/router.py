from fastapi import APIRouter
from training.router import router as training_router
from statistics.router import router as statistics_router
from user.router import router as user_router


router = APIRouter(
    prefix='/api/v1',
    tags=['v1']
)

router.include_router(user_router)
router.include_router(training_router)
router.include_router(statistics_router)
