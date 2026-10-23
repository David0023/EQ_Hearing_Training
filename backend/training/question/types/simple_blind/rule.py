from secrets import choice

from training.domain.rules import GeneratedQuestion, TrainingRule
from training.enums import QuestionType


class SimpleBlindRule(TrainingRule):
    question_type = QuestionType.SIMPLE_BLIND

    def __init__(self, frequencies: list[float], gains: list[float]):
        if not frequencies or not gains:
            raise ValueError("Simple blind settings must include frequencies and gains")
        self.frequencies = tuple(frequencies)
        self.gains = tuple(gains)

    def generate(self) -> GeneratedQuestion:
        return GeneratedQuestion(
            question_type=self.question_type,
            target_frequency=choice(self.frequencies),
            target_gain=choice(self.gains),
        )
