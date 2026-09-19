from pydantic import BaseModel, ConfigDict

class TrainingAttemptBase(BaseModel):
    pass

class GetAllTrainingAttempts(TrainingAttemptBase):
    model_config = ConfigDict(from_attributes=True)
    id: int