from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field

from training.enums import QuestionType
from training.question.types.simple_blind.schema import SimpleBlindAnswer


class ViewTrainingQuestion(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    sequence: int
    question_type: QuestionType
    target_frequency: float = Field(validation_alias=AliasPath("simple_blind", "target_frequency"))
    target_gain: float = Field(validation_alias=AliasPath("simple_blind", "target_gain"))
    user_frequency: float | None = Field(validation_alias=AliasPath("simple_blind", "user_frequency"))
    user_gain: float | None = Field(validation_alias=AliasPath("simple_blind", "user_gain"))
    is_answered: bool
    is_correct: bool | None
    answered_at: datetime | None


class GetTrainingQuestionResponse(BaseModel):
    question: ViewTrainingQuestion
    question_type: QuestionType


class GetAllTrainingQuestions(BaseModel):
    questions: list[ViewTrainingQuestion]


# The router accepts the active type's answer schema. Extend this to a
# discriminated union when another question type adds its answer schema.
AnswerQuestionRequest = SimpleBlindAnswer


class AnswerQuestionResponse(BaseModel):
    session_complete: bool
    question: ViewTrainingQuestion
