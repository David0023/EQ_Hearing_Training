from fastapi import APIRouter
from training.router import router as training_router
from training.info.router import router as frequency_router
from statistics.router import router as statistics_router

router = APIRouter(
    prefix='/api/vi',
    tags=['v1']
)

router.include_router(training_router)
router.include_router(frequency_router)
router.include_router(statistics_router)
