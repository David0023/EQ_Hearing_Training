from typing import TypedDict
from sqlalchemy.ext.asyncio import AsyncSession

from training.enums import QuestionType
from training.question.model import TrainingQuestion
from training.question.types.base import QuestionStrategy, PlanItem
from training.question.types.simple_blind import repository
from training.question.types.simple_blind.model import SimpleBlindQuestion
from training.question.types.simple_blind.rule import SimpleBlindRule
from training.question.types.schema import SimpleBlindAnswer
from training.domain.info import (
    STANDARD_GAIN_OPTIONS,
    validate_frequency,
    validate_gain,
)

class SimpleBlindSettings(TypedDict):
    min_frequency: float
    max_frequency: float
    min_gain: float
    max_gain: float


class SimpleBlindPlanItem(PlanItem):
    settings: SimpleBlindSettings


class SimpleBlindStrategy(QuestionStrategy):
    question_type = QuestionType.SIMPLE_BLIND

    def build_plan_item(
        self,
        count: int,
        settings: dict,
    ) -> SimpleBlindPlanItem:
        min_frequency = settings["min_frequency"]
        max_frequency = settings["max_frequency"]
        min_gain = settings["min_gain"]
        max_gain = settings["max_gain"]

        if not (validate_frequency(min_frequency) and validate_frequency(max_frequency)):
            raise ValueError("Invalid Frequency Option")
        if min_frequency > max_frequency:
            raise ValueError("Invalid Frequency Range")
        if not (validate_gain(min_gain) and validate_gain(max_gain)):
            raise ValueError("Invalid Gain Option")
        if min_gain > max_gain:
            raise ValueError("Invalid Gain Range")
        if not any(min_gain <= gain <= max_gain for gain in STANDARD_GAIN_OPTIONS):
            raise ValueError("Gain range has no available options")

        return {
            "question_type": self.question_type.value,
            "count": count,
            "settings": settings,
        }

    def generate_question(self, settings: SimpleBlindSettings) -> SimpleBlindQuestion:
        generated = SimpleBlindRule(
            min_frequency=settings["min_frequency"],
            max_frequency=settings["max_frequency"],
            min_gain=settings["min_gain"],
            max_gain=settings["max_gain"],
        ).generate()

        return SimpleBlindQuestion(
            target_frequency=generated.target_frequency,
            target_gain=generated.target_gain,
        )

    async def record_answer(
        self,
        db: AsyncSession,
        question: TrainingQuestion,
        answer: SimpleBlindAnswer,
    ) -> bool:
        detail = question.simple_blind
        if detail is None:
            raise ValueError("Simple blind question data is missing")

        is_correct = (
            detail.target_frequency == answer.user_frequency
            and detail.target_gain == answer.user_gain
        )

        await repository.record_answer(
            db,
            detail,
            user_frequency=answer.user_frequency,
            user_gain=answer.user_gain,
        )
        return is_correct

    def attach_question_detail(
        self,
        question: TrainingQuestion,
        detail: SimpleBlindQuestion,
    ) -> None:
        question.simple_blind = detail
