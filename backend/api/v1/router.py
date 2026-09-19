from fastapi import APIRouter
from api.v1.training import router as training_router
from api.v1.frequency import router as frequency_router

router = APIRouter(
    prefix='/api/vi',
    tags=['v1']
)

router.include_router(training_router)
router.include_router(frequency_router)