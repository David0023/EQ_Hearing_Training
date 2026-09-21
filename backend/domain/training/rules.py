from dataclasses import dataclass
from secrets import choice

from models.enums import QuestionType

@dataclass
class TrainingRule:
    frequencies: list[float]
    gain_level: float
    question_type: QuestionType

    def get_gain_options(self) -> tuple[float, ...]:
        """Return the negative, zero, and positive gain options."""
        return (
            -self.gain_level,
            0,
            self.gain_level,
        )

    def get_frequencies_options(self) -> tuple[float]:
        """Return the rule's frequencies as a tuple."""
        return tuple(self.frequencies)

    def get_random_gain(self) -> float:
        """Return a randomly selected gain option."""
        return choice(self.get_gain_options())

    def get_random_frequency(self) -> float:
        """Return a randomly selected frequency option."""
        return choice(self.get_frequencies_options())