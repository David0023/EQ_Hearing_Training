from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.enums import QuestionType

class TrainingQuestionBase(BaseModel):
    pass

class ViewTrainingQuestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_frequency: float
    target_gain: float
    user_frequency: float | None
    user_gain: float | None
    is_answered: bool
    answered_at: datetime | None

class GetTrainingQuestionResponse(BaseModel):
    question: ViewTrainingQuestion
    question_type: QuestionType

class GetAllTrainingQuestions(TrainingQuestionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class AnswerQuestionRequest(BaseModel):
    user_frequency: float 
    user_gain: float