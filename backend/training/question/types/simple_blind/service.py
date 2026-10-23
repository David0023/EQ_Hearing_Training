from typing import TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from training.enums import QuestionType
from training.question.types.simple_blind.rule import SimpleBlindRule
from training.question.types.simple_blind import repository
from training.question.types.simple_blind.model import SimpleBlindQuestion
from training.question.types.base import PlanItem
from training.question.model import TrainingQuestion
from training.question.types.simple_blind.schema import SimpleBlindAnswer

class SimpleBlindSettings(TypedDict):
    min_frequency: float
    max_frequency: float
    min_gain: float
    max_gain: float


class SimpleBlindPlanItem(PlanItem):
    settings: SimpleBlindSettings

def config(
    num_questions: int,
    min_frequency: float,
    max_frequency: float,
    min_gain: float,
    max_gain: float
):
    return {
        "question_type": QuestionType.SIMPLE_BLIND.value,
        "count": num_questions,
        "settings": {
            "min_frequency": min_frequency,
            "max_frequency": max_frequency,
            "min_gain": min_gain,
            "max_gain": max_gain,
        },
    }

def generate_question(block: SimpleBlindPlanItem) -> SimpleBlindQuestion:
    question_type = QuestionType(block["question_type"])
    if question_type is not QuestionType.SIMPLE_BLIND:
        raise ValueError(f"Unsupported question type: {question_type.value}")
    
    settings = block["settings"]
    generated = SimpleBlindRule(
        min_frequency=settings["min_frequency"],
        max_frequency=settings["max_frequency"],
        min_gain=settings["min_gain"],
        max_gain=settings["max_gain"]
    ).generate()

    return SimpleBlindQuestion(
        target_frequency=generated.target_frequency,
        target_gain=generated.target_gain,
    )

def check_answer(question: SimpleBlindQuestion, answer: SimpleBlindAnswer) -> bool:
    return (
        question.target_frequency == answer.user_frequency
        and question.target_gain == answer.user_gain
    )

async def record_answer(
    db: AsyncSession,
    question: TrainingQuestion,
    answer: SimpleBlindAnswer,
) -> bool:
    """Validate and persist a simple blind answer; return whether it is correct."""
    detail = question.simple_blind
    if detail is None:
        raise ValueError("Simple blind question data is missing")

    is_correct = check_answer(detail, answer)
    await repository.record_answer(
        db,
        detail,
        user_frequency=answer.user_frequency,
        user_gain=answer.user_gain,
    )
    return is_correct
