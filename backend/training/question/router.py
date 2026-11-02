from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from training.dependencies import get_locked_session, get_session_with_questions
from training.question import service
from training.question.schema import (
    GetTrainingQuestionResponse, AnswerQuestionRequest,
    GetAllTrainingQuestions, AnswerQuestionResponse
)
from training.session.model import TrainingSession
from training.question import repository
from training.question.model import TrainingQuestion
from training.question.schema import QuestionAnswerOptions

router = APIRouter(prefix="/sessions", tags=["questions"])

@router.get(
    "/{session_id}/questions",
    response_model=GetAllTrainingQuestions
)
async def get_all_questions(
    session: TrainingSession = Depends(get_session_with_questions),
):
    return GetAllTrainingQuestions(
        questions=session.training_questions,
    )

@router.post(
    "/{session_id}/questions/resume",
    status_code=status.HTTP_201_CREATED,
    response_model=GetTrainingQuestionResponse
)
async def start_question_or_continue(
    response: Response, db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    try:
        question, created = await service.get_or_create_question(db, session)
    except service.SessionCompletedException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session Completed. Could not start a new question")
    if not created:
        response.status_code = status.HTTP_200_OK
    return GetTrainingQuestionResponse(question=question, question_type=question.question_type)

@router.put(
    "/{session_id}/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    response_model=AnswerQuestionResponse
)
async def answer_question(
    question_id: int, form: AnswerQuestionRequest,
    db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    try:
        session_complete, question = await service.answer_question(db, session, question_id, form)
        return AnswerQuestionResponse(session_complete=session_complete, question=question)
    except service.QuestionAnswerException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except service.QuestionNotFoundException:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="The question could not be found.")


@router.get(
    "/{session_id}/questions/{question_id}/options",
    response_model=QuestionAnswerOptions,
)
async def get_question_answer_options(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    session: TrainingSession = Depends(get_locked_session),
):
    question = await repository.get_one(
        db, None,
        TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.id == question_id,
    )
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="The question could not be found.")

    try:
        options = service.get_question_answer_options(session, question)
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Question settings could not be found.")
    return QuestionAnswerOptions(question_type=question.question_type, **options)
