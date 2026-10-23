from abc import ABC, abstractmethod
from dataclasses import dataclass
from training.enums import QuestionType


@dataclass(frozen=True)
class GeneratedQuestion:
    question_type: QuestionType
    target_frequency: float
    target_gain: float


class TrainingRule(ABC):
    question_type: QuestionType

    @abstractmethod
    def generate(self) -> GeneratedQuestion:
        """Generate one question using this question type's settings."""
