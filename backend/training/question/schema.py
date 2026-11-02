from pydantic import BaseModel, Field

from training.enums import QuestionType
from training.question.types.schema import AnswerQuestionRequest, QuestionResponse

ViewTrainingQuestion = QuestionResponse

class GetTrainingQuestionResponse(BaseModel):
    question: ViewTrainingQuestion
    question_type: QuestionType


class GetAllTrainingQuestions(BaseModel):
    questions: list[ViewTrainingQuestion]


class AnswerQuestionResponse(BaseModel):
    session_complete: bool
    question: ViewTrainingQuestion


class QuestionAnswerOptions(BaseModel):
    question_type: QuestionType
    frequencies: list[float] = Field(default_factory=list)
    gains: list[float]
