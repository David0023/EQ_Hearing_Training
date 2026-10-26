from typing import Annotated
from pydantic import Field

from training.question.types.simple_blind.schema import SimpleBlindAnswer, SimpleBlindCreate, SimpleBlindQuestionResponse
from training.question.types.gain_blind.schema import GainBlindAnswer, GainBlindCreate, GainBlindQuestionResponse

AnswerQuestionRequest = Annotated[
    SimpleBlindAnswer | GainBlindAnswer,
    Field(discriminator="question_type"),
]

CreateQuestionRequest = Annotated[
    SimpleBlindCreate | GainBlindCreate,
    Field(discriminator="question_type"),
]

QuestionResponse = Annotated[
    SimpleBlindQuestionResponse | GainBlindQuestionResponse,
    Field(discriminator="question_type"),
]