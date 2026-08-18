from src.config import WAKE_WORD


def is_wake_word(text: str) -> bool:

    if not text:
        return False

    normalized = text.lower().strip()

    return WAKE_WORD in normalized
