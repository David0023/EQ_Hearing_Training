from typing import Literal
from datetime import datetime
from pydantic import AliasPath, BaseModel, ConfigDict, Field

class SimpleBlindAnswer(BaseModel):
    question_type: Literal["simple_blind"]
    user_frequency: float
    user_gain: float

class SimpleBlindCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Identify both the frequency and gain. Bounds are inclusive and must contain available options.",
            "examples": [
                {
                    "question_type": "simple_blind",
                    "min_frequency": 125,
                    "max_frequency": 1000,
                    "min_gain": 3,
                    "max_gain": 6,
                }
            ],
        }
    )

    question_type: Literal["simple_blind"] = Field(
        description="Selects the simple blind setting format."
    )
    min_frequency: float = Field(description="Lowest allowed frequency (inclusive).")
    max_frequency: float = Field(description="Highest allowed frequency (inclusive).")
    min_gain: float = Field(description="Lowest allowed positive gain bound (inclusive).")
    max_gain: float = Field(description="Highest allowed positive gain bound (inclusive).")

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
