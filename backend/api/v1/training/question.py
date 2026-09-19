from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.training_question import GetTrainingQuestionResponse

from services.training import create_training_question
from core.dependencies import get_db, get_current_user
from models.user import User
from repositories import training_session
from repositories import training_question

router = APIRouter(
    prefix='/question',
    tags=['training']
)
##---------------------------------------
@router.post('/{session_id}', 
    status_code=status.HTTP_201_CREATED,
    response_model=GetTrainingQuestionResponse
)
async def start_question_or_continue(
    response: Response,
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = await training_session.get_one(db, id=session_id)

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")

    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")

    unanswered_question = await training_question.get_one(
        db,
        training_session_id=session.id,
        is_answered=False
    )
    if unanswered_question:
        response.status_code = status.HTTP_200_OK
        return GetTrainingQuestionResponse(
            question=unanswered_question,
            question_type=session.question_type
        )

    return GetTrainingQuestionResponse(
        question=await create_training_question(db, session),
        question_type=session.question_type
    )

@router.put('/{session_id}/{question_id}', 
    status_code=status.HTTP_200_OK,
)
async def answer_question(
    session_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ... ## TODO: Implement