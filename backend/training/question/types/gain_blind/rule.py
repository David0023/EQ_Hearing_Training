from secrets import choice

from training.enums import QuestionType
from training.question.types.base import GeneratedQuestion, QuestionRule
from training.domain.info import get_all_gain, get_frequency_range


class GainBlindRule(QuestionRule):
    question_type = QuestionType.GAIN_BLIND

    def __init__(
        self,
        min_frequency: float,
        max_frequency: float,
    ):
        frequencies = get_frequency_range(min_frequency, max_frequency)

        if not frequencies:
            raise ValueError("Simple blind settings must include frequencies and gains")
        self.frequencies = tuple(frequencies)
        self.gains = tuple(get_all_gain(include_negative=True, include_zero=True))

    def generate(self) -> GeneratedQuestion:
        return GeneratedQuestion(
            question_type=self.question_type,
            target_frequency=choice(self.frequencies),
            target_gain=choice(self.gains),
        )
