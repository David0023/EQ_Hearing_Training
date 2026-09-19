from dataclasses import dataclass
from domain.training.rules import TrainingRule

@dataclass
class TrainingQuestion:
    frequency: float
    gain: float

def generate_question(
    training_rule: TrainingRule
) -> TrainingQuestion | None:
    return TrainingQuestion(
        frequency=training_rule.get_random_frequency(), 
        gain=training_rule.get_random_gain()
    )