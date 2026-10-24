from abc import ABC, abstractmethod
from typing import TypedDict, Protocol, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from training.question.model import TrainingQuestion


from training.enums import QuestionType


class PlanItem(TypedDict):
    question_type: str
    count: int
    settings: dict

@dataclass(frozen=True)
class GeneratedQuestion:
    question_type: QuestionType
    target_frequency: float
    target_gain: float

class QuestionRule(ABC):
    question_type: QuestionType

    @abstractmethod
    def generate(self) -> GeneratedQuestion:
        """Generate one question using this question type's settings."""


class QuestionStrategy(Protocol):
    question_type: QuestionType

    def build_plan_item(self, count: int, settings: Any) -> PlanItem: ...

    def generate_question(self, settings: Any) -> Any: ...

    async def record_answer(
        self,
        db: AsyncSession,
        question: TrainingQuestion,
        answer: Any,
    ) -> bool: ...

    def attach_question_detail(self, question: TrainingQuestion, detail: Any) -> None: ...
