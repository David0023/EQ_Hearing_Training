from training.domain.rules import GeneratedQuestion, TrainingRule


def generate_question(training_rule: TrainingRule) -> GeneratedQuestion:
    """Generate one question through its question-type-specific rule."""
    return training_rule.generate()
