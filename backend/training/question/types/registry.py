from training.enums import QuestionType
from training.question.types.base import QuestionStrategy
from training.question.types.simple_blind.strategy import SimpleBlindStrategy

STRATEGIES: dict[QuestionType, QuestionStrategy] = {
    QuestionType.SIMPLE_BLIND: SimpleBlindStrategy(),
}

def get_strategy(question_type: QuestionType) -> QuestionStrategy:
    try:
        return STRATEGIES[question_type]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported question type: {question_type.value}"
        ) from exc
