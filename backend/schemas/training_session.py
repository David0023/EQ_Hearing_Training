from pydantic import BaseModel, ConfigDict
from datetime import datetime
from models.enums import QuestionType
from schemas.training_attempt import GetAllTrainingAttempts

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

class GetTrainingSessionWithAttemptsResponse(GetTrainingSessionResponse):
    training_attempts: list[GetAllTrainingAttempts]

class GetAllTrainingSessionsResponse(BaseModel):
    sessions: list[GetTrainingSessionResponse]