from pydantic import BaseModel

class FrequencyGroupItem(BaseModel):
    name: str
    frequencies: list[float]

class FrequencyGroupResponse(BaseModel):
    available_groups: list[FrequencyGroupItem]

class GainOptionResponse(BaseModel):
    gain_options = list[float]