from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from training.enums import QuestionType, SessionStatus
from training.question.schema import ViewTrainingQuestion

class TrainingSessionBase(BaseModel):
    num_questions: int
    question_type: QuestionType
    min_frequency: float
    max_frequency: float
    gain_level: float

class TrainingSessionCreateRequest(BaseModel):
    num_questions: int = Field(gt=5)
    question_type: QuestionType
    min_frequency: float
    max_frequency: float
    gain_level: float

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

class SessionResultPerFrequency(BaseModel):
    frequency: float
    accuracy: float
    n_total: int
    n_correct: int