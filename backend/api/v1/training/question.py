from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, get_current_user
from models.user import User
from models.training_question import TrainingQuestion
from repositories import training_session, training_question
from schemas.training_question import GetTrainingQuestionResponse, AnswerQuestionRequest, ViewTrainingQuestion
from services.training import create_training_question

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
    session = await training_session.get_one_with_questions(db, id=session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")

    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")

    unanswered_questions = [
        q for q in session.training_questions
        if not q.is_answered
    ]
    if unanswered_questions:
        response.status_code = status.HTTP_200_OK
        return GetTrainingQuestionResponse(
            question=unanswered_questions[0],
            question_type=session.question_type
        )

    return GetTrainingQuestionResponse(
        question=await create_training_question(db, session),
        question_type=session.question_type
    )

@router.put('/{session_id}/{question_id}', 
    status_code=status.HTTP_200_OK,
    response_model=ViewTrainingQuestion
)
async def answer_question(
    session_id: int,
    question_id: int,
    form: AnswerQuestionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = await training_session.get_one_with_questions(db, id=session_id)
    if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-existing training session")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not accessible")

    matching_questions: list[TrainingQuestion] = [
        q for q in session.training_questions
        if q.id == question_id
    ]
    if not matching_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The question do not belong to this session"
        )
    question = matching_questions[0]
    if question.is_answered:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This question is already completed"
        )
    await training_question.update(
        db, question,
        user_frequency=form.user_frequency,
        user_gain=form.user_gain,
        is_answered=True,
        answered_at=datetime.now(timezone.utc)
    )

    return question
