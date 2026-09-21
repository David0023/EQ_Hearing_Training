def calculate_difficulty(
    frequency_count: int,
    gain_level: float,
    question_type: str,
) -> float:
    """Calculate difficulty from the gain level and frequency count."""
    return gain_level * frequency_count ## TODO: Add a proper logic here