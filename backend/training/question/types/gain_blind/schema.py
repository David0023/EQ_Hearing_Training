from typing import Literal
from datetime import datetime
from pydantic import AliasPath, BaseModel, ConfigDict, Field

class GainBlindAnswer(BaseModel):
    question_type: Literal["gain_blind"]
    user_gain: float

class GainBlindCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Identify the gain at a randomly selected frequency. The backend chooses the target gain from all available values.",
            "examples": [
                {
                    "question_type": "gain_blind",
                    "min_frequency": 125,
                    "max_frequency": 1000,
                }
            ],
        }
    )

    question_type: Literal["gain_blind"] = Field(
        description="Selects the gain blind setting format."
    )
    min_frequency: float = Field(description="Lowest allowed frequency (inclusive).")
    max_frequency: float = Field(description="Highest allowed frequency (inclusive).")

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
