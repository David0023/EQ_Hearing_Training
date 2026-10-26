from typing import Literal
from datetime import datetime
from pydantic import AliasPath, BaseModel, ConfigDict, Field

class GainBlindAnswer(BaseModel):
    question_type: Literal["gain_blind"]
    user_gain: float

class GainBlindCreate(BaseModel):
    question_type: Literal["gain_blind"]
    min_frequency: float
    max_frequency: float

class GainBlindQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question_type: Literal["gain_blind"]
    id: int
    training_session_id: int
    sequence: int
    is_answered: bool
    is_correct: bool | None
    answered_at: datetime | None
    target_frequency: float = Field(validation_alias=AliasPath("gain_blind", "frequency"))
    target_gain: float = Field(validation_alias=AliasPath("gain_blind", "target_gain"))
    user_gain: float | None = Field(validation_alias=AliasPath("gain_blind", "user_gain"))
