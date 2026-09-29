from dataclasses import dataclass
from training.domain.rules import TrainingRule
from training.enums import QuestionType

@dataclass
class TrainingQuestion:
    frequency: float
    gain: float
    question_type: QuestionType

def generate_question(
    training_rule: TrainingRule
) -> TrainingQuestion:
    """Generate a question using random values from a training rule."""
    return TrainingQuestion(
        frequency=training_rule.get_random_frequency(),
        gain=training_rule.get_random_gain(),
        question_type=training_rule.question_type
    )
