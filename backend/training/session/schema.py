from pydantic import BaseModel, ConfigDict
from datetime import datetime
from training.enums import QuestionType, SessionStatus
from training.question.schema import ViewTrainingQuestion

class TrainingSessionBase(BaseModel):
    num_questions: int
    question_type: QuestionType
    min_frequency: float
    max_frequency: float
    gain_level: float

class TrainingSessionCreateRequest(TrainingSessionBase):
    pass

class TrainingSessionInfo(TrainingSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_status: SessionStatus
    started_at: datetime
    last_accessed_at: datetime | None
    completed_at: datetime | None

class TrainingSessionCreateResponse(TrainingSessionInfo):
    pass

class TrainingSessionWithQuestion(TrainingSessionInfo):
    training_questions: list[ViewTrainingQuestion]

class TrainingSessionSummary(BaseModel):
    session: TrainingSessionInfo
    answered_count: int
    correct_count: int
    accuracy: float

class TrainingSessionSummaryList(BaseModel):
    sessions: list[TrainingSessionSummary]
