"""Import all mapped classes before metadata creation or mapper configuration."""
from user.model import User
from training.session.model import TrainingSession
from training.question.model import TrainingQuestion

__all__ = ["User", "TrainingSession", "TrainingQuestion"]
