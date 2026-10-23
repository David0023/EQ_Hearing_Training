from pydantic import BaseModel


class SimpleBlindAnswer(BaseModel):
    user_frequency: float
    user_gain: float
