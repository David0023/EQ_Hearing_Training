STANDARD_FREQUENCIES: tuple[float] = (
    31.5,
    63,
    125,
    250,
    500,
    1000,
    2000,
    4000,
    8000,
    16000,
)

FREQUENCY_GROUPS: dict[str, tuple[float, float]] = {
    "sub_bass": (31.5, 63),
    "bass": (125, 250),
    "low_mid": (500,500),
    "mid": (1000,1000),
    "upper_mid": (2000, 4000),
    "high": (8000,8000),
    "air": (16000,16000),
}

STANDARD_GAIN_OPTIONS: tuple[float] = (
    1.5,
    3.0,
    4.5,
    6.0,
    7.5,
    9.0,
    10.5,
    13.0,
    14.5,
    15.0
)

def validate_frequency(frequency: float) -> bool:
    """Return whether a frequency is one of the standard frequencies."""
    return frequency in STANDARD_FREQUENCIES

def validate_gain(gain: float) -> bool:
    """Return whether a gain is one of the standard gain options."""
    return gain in STANDARD_GAIN_OPTIONS

def get_frequency_range(min_frequency: float, max_frequency: float) -> list[float]:
    """Return standard frequencies within the inclusive frequency range."""
    return [i for i in STANDARD_FREQUENCIES if min_frequency <= i <= max_frequency]

def get_frequency_range_by_name(min_group: str, max_group: str) -> list[float]:
    """Return standard frequencies spanning two named frequency groups."""
    min_range = FREQUENCY_GROUPS.get(min_group)
    max_range = FREQUENCY_GROUPS.get(max_group)

    if not min_range or not max_range:
        return []

    return get_frequency_range(min_range[0], max_range[1])