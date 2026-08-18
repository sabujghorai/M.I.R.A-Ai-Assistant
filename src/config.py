import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


GEMINI_MODEL = "gemini-3-flash-preview"


# ============================================================
# ASSISTANT
# ============================================================

ASSISTANT_NAME = "Mira"

WAKE_WORD = "hey mira"


# ============================================================
# VOICE
# ============================================================

DEFAULT_LANGUAGE = "en-IN"


# ============================================================
# AUDIO
# ============================================================

ACTIVATION_SOUND = (
    "sounds/siri-sound-effect.mp3"
)
