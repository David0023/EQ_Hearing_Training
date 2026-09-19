from pydantic import BaseModel, ConfigDict
from datetime import datetime
from models.enums import QuestionType
from schemas.training_question import GetAllTrainingQuestions

class TrainingSessionBase(BaseModel):
    question_type: QuestionType
    min_frequency: float
    max_frequency: float
    gain_level: float

class TrainingSessionCreateRequest(TrainingSessionBase):
    pass

class TrainingSessionCreateResponse(TrainingSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    started_at: datetime
    completed_at: datetime | None

class GetTrainingSessionResponse(TrainingSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    started_at: datetime
    completed_at: datetime | None

class GetTrainingSessionWithQuestionsResponse(GetTrainingSessionResponse):
    training_questions: list[GetAllTrainingQuestions]

class GetAllTrainingSessionsResponse(BaseModel):
    sessions: list[GetTrainingSessionResponse]