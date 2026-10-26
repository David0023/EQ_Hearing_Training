from typing import TypedDict
from sqlalchemy.ext.asyncio import AsyncSession

from training.enums import QuestionType
from training.question.model import TrainingQuestion
from training.question.types.base import QuestionStrategy, PlanItem
from training.question.types.gain_blind import repository
from training.question.types.gain_blind.model import GainBlindQuestion
from training.question.types.gain_blind.rule import GainBlindRule
from training.question.types.gain_blind.schema import GainBlindAnswer
from training.domain.info import (
    validate_frequency,
)

class GainBlindSettings(TypedDict):
    min_frequency: float
    max_frequency: float

class GainBlindPlanItem(PlanItem):
    settings: GainBlindSettings


class GainBlindStrategy(QuestionStrategy):
    question_type = QuestionType.GAIN_BLIND

    def build_plan_item(
        self,
        count: int,
        settings: dict,
    ) -> GainBlindPlanItem:
        min_frequency = settings["min_frequency"]
        max_frequency = settings["max_frequency"]

        if not (validate_frequency(min_frequency) and validate_frequency(max_frequency)):
            raise ValueError("Invalid Frequency Option")
        if min_frequency > max_frequency:
            raise ValueError("Invalid Frequency Range")

        return {
            "question_type": self.question_type.value,
            "count": count,
            "settings": settings,
        }

    def generate_question(self, settings: GainBlindSettings) -> GainBlindQuestion:
        generated = GainBlindRule(
            min_frequency=settings["min_frequency"],
            max_frequency=settings["max_frequency"],
        ).generate()

        return GainBlindQuestion(
            frequency=generated.target_frequency,
            target_gain=generated.target_gain,
        )

    async def record_answer(
        self,
        db: AsyncSession,
        question: TrainingQuestion,
        answer: GainBlindAnswer,
    ) -> bool:
        detail = question.gain_blind
        if detail is None:
            raise ValueError("Gain blind question data is missing")
        await repository.record_answer(
            db,
            detail,
            user_gain=answer.user_gain,
        )
        return detail.target_gain == answer.user_gain

    def attach_question_detail(
        self,
        question: TrainingQuestion,
        detail: GainBlindQuestion,
    ) -> None:
        question.gain_blind = detail
