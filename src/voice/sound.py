import os
import subprocess

from src.config import ACTIVATION_SOUND


def play_activation_sound():

    sound_path = os.path.abspath(
        ACTIVATION_SOUND
    )

    if not os.path.exists(sound_path):

        print(
            f"Activation sound not found: "
            f"{sound_path}"
        )

        return

    try:

        subprocess.Popen(
            ["afplay", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as error:

        print(
            "Activation sound error:",
            error
        )