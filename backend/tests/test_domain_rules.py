import pytest
from types import SimpleNamespace

from training.domain.difficulty import calculate_difficulty
from training.domain.info import (
    get_all_gain,
    get_frequency_range,
    get_frequency_range_by_name,
    get_gain_range,
    validate_frequency,
    validate_gain,
)
from training.enums import QuestionType
from training.question.types.gain_blind.rule import GainBlindRule
from training.question.types.registry import get_strategy
from training.question.types.simple_blind.rule import SimpleBlindRule
from training.question.types.simple_blind.schema import SimpleBlindAnswer
from training.question.types.gain_blind.schema import GainBlindAnswer
import db.models  # noqa: F401  # Register ORM relationships before constructing mapped objects.


def test_frequency_and_gain_ranges_include_only_supported_values():
    assert validate_frequency(125)
    assert not validate_frequency(126)
    assert validate_gain(3)
    assert not validate_gain(2)
    assert get_frequency_range(125, 500) == [125, 250, 500]
    assert get_gain_range(3, 6) == [-3, -4.5, -6, 3, 4.5, 6]
    assert get_gain_range(3, 3, include_negative=False, include_zero=True) == [0, 3]
    assert get_all_gain(include_negative=False) == [1.5, 3, 4.5, 6, 7.5, 9]
    assert get_frequency_range_by_name("bass", "mid") == [125, 250, 500, 1000]
    assert get_frequency_range_by_name("unknown", "mid") == []


def test_difficulty_calculation():
    assert calculate_difficulty(3, 4.5, "simple_blind") == 13.5


def test_simple_blind_rule_validates_and_generates_within_bounds():
    rule = SimpleBlindRule(125, 250, 3, 4.5)
    generated = rule.generate()
    assert generated.question_type == QuestionType.SIMPLE_BLIND
    assert generated.target_frequency in (125, 250)
    assert generated.target_gain in (-3, -4.5, 3, 4.5)
    with pytest.raises(ValueError):
        SimpleBlindRule(126, 249, 3, 4.5)
    with pytest.raises(ValueError):
        SimpleBlindRule(125, 250, 0.5, 1)


def test_gain_blind_rule_includes_zero_and_validates_frequency():
    generated = GainBlindRule(500, 500).generate()
    assert generated.question_type == QuestionType.GAIN_BLIND
    assert generated.target_frequency == 500
    assert generated.target_gain in (-9, -7.5, -6, -4.5, -3, -1.5, 0, 1.5, 3, 4.5, 6, 7.5, 9)
    with pytest.raises(ValueError):
        GainBlindRule(501, 800)


def test_strategy_registry_and_plan_validation():
    simple = get_strategy(QuestionType.SIMPLE_BLIND)
    gain = get_strategy(QuestionType.GAIN_BLIND)
    assert simple.build_plan_item(2, {
        "min_frequency": 125, "max_frequency": 250,
        "min_gain": 3, "max_gain": 4.5,
    })["count"] == 2
    assert gain.build_plan_item(3, {"min_frequency": 125, "max_frequency": 250})["count"] == 3
    with pytest.raises(ValueError, match="Invalid Frequency Option"):
        gain.build_plan_item(1, {"min_frequency": 126, "max_frequency": 250})
    with pytest.raises(ValueError, match="Invalid Frequency Range"):
        simple.build_plan_item(1, {
            "min_frequency": 250, "max_frequency": 125,
            "min_gain": 3, "max_gain": 4.5,
        })
    with pytest.raises(ValueError, match="Invalid Gain Option"):
        simple.build_plan_item(1, {
            "min_frequency": 125, "max_frequency": 250,
            "min_gain": 2, "max_gain": 4.5,
        })
    with pytest.raises(ValueError, match="Invalid Gain Range"):
        simple.build_plan_item(1, {
            "min_frequency": 125, "max_frequency": 250,
            "min_gain": 4.5, "max_gain": 3,
        })


def test_strategies_generate_questions_and_answer_options():
    simple = get_strategy(QuestionType.SIMPLE_BLIND)
    generated_simple = simple.generate_question({
        "min_frequency": 125, "max_frequency": 250,
        "min_gain": 3, "max_gain": 4.5,
    })
    assert generated_simple.target_frequency in (125, 250)
    assert simple.get_answer_options({
        "min_frequency": 125, "max_frequency": 250,
        "min_gain": 3, "max_gain": 4.5,
    })["frequencies"] == [125, 250]

    gain = get_strategy(QuestionType.GAIN_BLIND)
    generated_gain = gain.generate_question({"min_frequency": 500, "max_frequency": 500})
    assert generated_gain.frequency == 500
    assert 0 in gain.get_answer_options({"min_frequency": 500, "max_frequency": 500})["gains"]


@pytest.mark.anyio
async def test_strategy_answer_recording(monkeypatch):
    async def record_answer(*args, **kwargs):
        return None

    simple = get_strategy(QuestionType.SIMPLE_BLIND)
    monkeypatch.setattr("training.question.types.simple_blind.strategy.repository.record_answer", record_answer)
    question = SimpleNamespace(simple_blind=SimpleNamespace(target_frequency=125, target_gain=3))
    assert await simple.record_answer(None, question, SimpleBlindAnswer(
        question_type="simple_blind", user_frequency=125, user_gain=3,
    ))
    assert not await simple.record_answer(None, question, SimpleBlindAnswer(
        question_type="simple_blind", user_frequency=250, user_gain=3,
    ))
    question.simple_blind = None
    with pytest.raises(ValueError, match="data is missing"):
        await simple.record_answer(None, question, SimpleBlindAnswer(
            question_type="simple_blind", user_frequency=125, user_gain=3,
        ))

    gain = get_strategy(QuestionType.GAIN_BLIND)
    monkeypatch.setattr("training.question.types.gain_blind.strategy.repository.record_answer", record_answer)
    question = SimpleNamespace(gain_blind=SimpleNamespace(target_gain=-3))
    assert await gain.record_answer(None, question, GainBlindAnswer(question_type="gain_blind", user_gain=-3))
    assert not await gain.record_answer(None, question, GainBlindAnswer(question_type="gain_blind", user_gain=3))
    question.gain_blind = None
    with pytest.raises(ValueError, match="data is missing"):
        await gain.record_answer(None, question, GainBlindAnswer(question_type="gain_blind", user_gain=0))
