from typing import Annotated, Literal
from pydantic import BaseModel, Field

class SimpleBlindAnswer(BaseModel):
    question_type: Literal["simple_blind"]
    user_frequency: float
    user_gain: float

class SimpleBlindCreate(BaseModel):
    question_type: Literal["simple_blind"]
    min_frequency: float
    max_frequency: float
    min_gain: float
    max_gain: float

## TODO: Replace this with actual type
class AnotherAnswer(BaseModel):
    question_type: Literal["another_type"]
    user_frequency: float

class AnotherCreate(BaseModel):
    question_type: Literal["another_type"]
    gain_lv: float

AnswerQuestionRequest = Annotated[
    SimpleBlindAnswer | AnotherAnswer,
    Field(discriminator="question_type"),
]

CreateQuestionRequest = Annotated[
    SimpleBlindCreate | AnotherCreate,
    Field(discriminator="question_type"),
]


