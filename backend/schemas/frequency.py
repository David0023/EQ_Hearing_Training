from pydantic import BaseModel, ConfigDict

class FrequencyGroupItem(BaseModel):
    name: str
    frequencies: list[float]

class FrequencyGroupResponse(BaseModel):
    available_groups: list[FrequencyGroupItem]