from typing import Literal
from datetime import datetime
from pydantic import AliasPath, BaseModel, ConfigDict, Field

class SimpleBlindAnswer(BaseModel):
    question_type: Literal["simple_blind"]
    user_frequency: float
    user_gain: float

class SimpleBlindCreate(BaseModel):
    question_type: Literal["simple_blind"]
    min_frequency: float
    max_frequency: float
    min_gain: float
    max_gain: float

class SimpleBlindQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question_type: Literal["simple_blind"]
    id: int
    training_session_id: int
    sequence: int
    is_answered: bool
    is_correct: bool | None
    answered_at: datetime | None
    target_frequency: float = Field(validation_alias=AliasPath("simple_blind", "target_frequency"))
    target_gain: float = Field(validation_alias=AliasPath("simple_blind", "target_gain"))
    user_frequency: float | None = Field(validation_alias=AliasPath("simple_blind", "user_frequency"))
    user_gain: float | None = Field(validation_alias=AliasPath("simple_blind", "user_gain"))
