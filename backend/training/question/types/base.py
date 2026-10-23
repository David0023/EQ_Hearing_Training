from typing import TypedDict
from abc import ABC, abstractmethod
from dataclasses import dataclass

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
