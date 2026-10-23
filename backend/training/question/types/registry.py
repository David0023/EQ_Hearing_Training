from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from training.enums import QuestionType
from training.question.model import TrainingQuestion
from training.question.schema import AnswerQuestionRequest
from training.question.types.simple_blind import service as simple_blind_service


AnswerService = Callable[
    [AsyncSession, TrainingQuestion, AnswerQuestionRequest], Awaitable[bool]
]

ANSWER_SERVICES: dict[QuestionType, AnswerService] = {
    QuestionType.SIMPLE_BLIND: simple_blind_service.record_answer,
}


def get_answer_service(question_type: QuestionType) -> AnswerService:
    """Return the answer handler registered for a question type."""
    try:
        return ANSWER_SERVICES[question_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported question type: {question_type.value}") from exc
