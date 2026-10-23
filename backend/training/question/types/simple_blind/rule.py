from secrets import choice

from training.enums import QuestionType
from training.question.types.base import GeneratedQuestion, QuestionRule
from training.domain.info import STANDARD_GAIN_OPTIONS, get_frequency_range


class SimpleBlindRule(QuestionRule):
    question_type = QuestionType.SIMPLE_BLIND

    def __init__(
        self,
        min_frequency: float,
        max_frequency: float,
        min_gain: float,
        max_gain: float,
    ):
        frequencies = get_frequency_range(min_frequency, max_frequency)
        gain_options = [
            gain for gain in STANDARD_GAIN_OPTIONS
            if min_gain <= gain <= max_gain
        ]
        gains = [-gain for gain in gain_options] + gain_options

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
