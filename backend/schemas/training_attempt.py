from pydantic import BaseModel, ConfigDict
from models.enums import QuestionType

class TrainingAttemptBase(BaseModel):
    pass

class ViewTrainingAttmpt(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_frequency: float
    target_gain: float
    is_answered: bool

class GetTrainingAttmptResponse(BaseModel):
    attempt: ViewTrainingAttmpt
    question_type: QuestionType

class GetAllTrainingAttempts(TrainingAttemptBase):
    model_config = ConfigDict(from_attributes=True)
    id: int