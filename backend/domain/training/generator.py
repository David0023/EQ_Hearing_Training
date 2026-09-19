from dataclasses import dataclass
from domain.training.rules import TrainingRule
from models.enums import QuestionType

@dataclass
class TrainingQuestion:
    frequency: float
    gain: float
    question_type: QuestionType

def generate_question(
    training_rule: TrainingRule
) -> TrainingQuestion:
    return TrainingQuestion(
        frequency=training_rule.get_random_frequency(), 
        gain=training_rule.get_random_gain(),
        question_type=training_rule.question_type
    )