from enum import Enum

class QuestionType(str, Enum):
    SIMPLE_BLIND = 'simple_blind'

class SessionStatus(str, Enum):
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'