from enum import Enum

class QuestionType(str, Enum):
    PERFECT_BLIND = 'perfect_blind'
    GAIN_BLIND = 'gain_blind'