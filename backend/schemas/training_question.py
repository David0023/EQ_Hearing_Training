from pydantic import BaseModel, ConfigDict
from models.enums import QuestionType

class TrainingQuestionBase(BaseModel):
    pass

class ViewTrainingQuestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_frequency: float
    target_gain: float
    is_answered: bool

class GetTrainingQuestionResponse(BaseModel):
    question: ViewTrainingQuestion
    question_type: QuestionType

class GetAllTrainingQuestions(TrainingQuestionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int