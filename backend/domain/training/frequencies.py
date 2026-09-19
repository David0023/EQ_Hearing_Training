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

def validate_frequency(frequency: float) -> bool:
    return frequency in STANDARD_FREQUENCIES

def get_frequency_range(min_frequency: float, max_frequency: float) -> list[float]:
    return [i for i in STANDARD_FREQUENCIES if min_frequency <= i <= max_frequency]

def get_frequency_range_by_name(min_group: str, max_group: str) -> list[float]:
    min_range = FREQUENCY_GROUPS.get(min_group)
    max_range = FREQUENCY_GROUPS.get(max_group)

    if not min_range or not max_range:
        return []

    return get_frequency_range(min_range[0], max_range[1])