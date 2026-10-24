from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from training.enums import SessionStatus
from training.question.schema import ViewTrainingQuestion
from training.question.types.schema import CreateQuestionRequest


class SessionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    num_questions: int
    config: dict
    session_status: SessionStatus
    started_at: datetime
    last_accessed_at: datetime | None
    completed_at: datetime | None


class SessionCreateRequest(BaseModel):
    num_questions: int = Field(gt=0)
    setting: CreateQuestionRequest


class SessionCreateResponse(SessionBase):
    pass


class SessionWithQuestions(SessionBase):
    training_questions: list[ViewTrainingQuestion]


class SessionSummary(BaseModel):
    session: SessionBase
    answered_count: int
    correct_count: int
    accuracy: float


class TrainingSessionSummaryList(BaseModel):
    sessions: list[SessionSummary]


class SessionResultPerFrequency(BaseModel):
    frequency: float
    accuracy: float
    n_total: int
    n_correct: int
