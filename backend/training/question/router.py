from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from training.dependencies import get_locked_session, get_session_with_questions
from training.question import service
from training.question.schema import (
    GetTrainingQuestionResponse, AnswerQuestionRequest, ViewTrainingQuestion,
    GetAllTrainingQuestions,
)
from training.session.model import TrainingSession

router = APIRouter(prefix="/question", tags=["training"])


@router.get("/all/{session_id}", response_model=GetAllTrainingQuestions)
async def get_all_questions(
    session: TrainingSession = Depends(get_session_with_questions),
):
    return GetAllTrainingQuestions(
        questions=session.training_questions, question_type=session.question_type,
    )


@router.post("/{session_id}", status_code=status.HTTP_201_CREATED,
             response_model=GetTrainingQuestionResponse)
async def start_question_or_continue(
    response: Response, db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    question, created = await service.get_or_create_question(db, session)
    if not created:
        response.status_code = status.HTTP_200_OK
    return GetTrainingQuestionResponse(question=question, question_type=session.question_type)


@router.put("/{session_id}/{question_id}", response_model=ViewTrainingQuestion)
async def answer_question(
    question_id: int, form: AnswerQuestionRequest,
    db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    return await service.answer_question(db, session, question_id, form)
