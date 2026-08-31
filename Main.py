"""
Main.py — Entry point that wires together all Backend modules for M.I.R.A.

Flow per loop iteration:
    1. Get a query (voice via Backend.SpeechToText, or typed fallback if
       voice isn't available).
    2. Classify it with Backend.Model.FirstLayerDMM -> list of tagged
       sub-queries, e.g. ["open chrome", "general how are you"].
    3. Route each sub-query to the right handler:
         - "general ..."          -> Backend.Chatbot.ChatBot
         - "realtime ..."         -> Backend.RealtimeSearchEngine.RealtimeSearchEngine
         - "open/close/play/system/content/google search/youtube search/
            make|create a folder|file ..." -> Backend.Automation.Automation
         - "generate image ..."   -> writes to Frontend/Files/ImageGeneration.data
                                      and launches Backend/ImageGeneration.py as
                                      a one-shot subprocess. That script polls
                                      the .data file and exits after one
                                      generation; importing it directly instead
                                      would hang Main.py, since it runs a
                                      blocking while-loop at import time.
         - "reminder ..."         -> not implemented in Automation.py yet;
                                      logged and reported to the user instead
                                      of silently doing nothing.
         - "exit ..."             -> says goodbye and stops the loop.
    4. Speaks + prints the response with Backend.TextToSpeech.

NOTE: This does not yet talk to Frontend/GUI.py (haven't seen that file).
It runs as a plain terminal (+ voice, if available) loop.
"""

import asyncio
import os
import subprocess
import sys
import traceback

from dotenv import dotenv_values

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.TextToSpeech import TextToSpeach

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# --- Speech input is optional. SpeechToText.py launches a headless Chrome
# browser the moment it is imported (module-level `driver = webdriver.Chrome(...)`).
# If Chrome/chromedriver isn't set up correctly, that import raises — so we
# guard it and fall back to typed input instead of crashing the whole assistant.
try:
    from Backend.SpeechToText import SpeechRecognition, SetAssistantStatus
    VOICE_AVAILABLE = True
except Exception as e:
    print(f"[Main] Voice input unavailable, falling back to typed input: {e}")
    VOICE_AVAILABLE = False

    def SetAssistantStatus(_status):
        pass

FRONTEND_FILES_DIR = os.path.join(os.getcwd(), "Frontend", "Files")
IMAGE_DATA_FILE = os.path.join(FRONTEND_FILES_DIR, "ImageGeneration.data")
os.makedirs(FRONTEND_FILES_DIR, exist_ok=True)


def GetQuery() -> str:
    """Get one query from voice if available, else typed input."""
    if VOICE_AVAILABLE:
        SetAssistantStatus("Listening...")
        text = SpeechRecognition()
        if text:
            print(f"{Username}: {text}")
            return text
        return ""
    return input(f"{Username}: ").strip()


def Speak(text: str):
    print(f"{Assistantname}: {text}")
    try:
        TextToSpeach(text)
    except Exception as e:
        # Don't let a broken audio backend (e.g. missing pygame) kill the loop.
        print(f"[Main] TTS failed, continuing without audio: {e}")


def RequestImage(prompt: str):
    """Hand a prompt off to ImageGeneration.py, which runs as its own
    one-shot process (see module docstring above for why)."""
    with open(IMAGE_DATA_FILE, "w") as f:
        f.write(f"{prompt},True")
    subprocess.Popen(
        [sys.executable, os.path.join("Backend", "ImageGeneration.py")]
    )
    Speak(f"Generating an image of {prompt}, sir.")


def HandleDecision(decisions: list[str]) -> bool:
    """Route each classified sub-query to its handler. Returns False to stop the loop."""
    general_query = None
    realtime_query = None
    automation_cmds = []

    for decision in decisions:
        if decision.startswith("exit"):
            Speak("Goodbye, sir.")
            return False

        elif decision.startswith("generate image "):
            RequestImage(decision.removeprefix("generate image ").strip())

        elif decision.startswith("reminder "):
            # Automation.py has no reminder handler yet — report instead of
            # silently doing nothing.
            print(f"[Main] Reminder requested but not implemented: {decision}")
            Speak("I can't set reminders yet, sir — that part isn't built.")

        elif decision.startswith("general "):
            # ChatBot() is single-turn per call; only act on the first one.
            if general_query is None:
                general_query = decision.removeprefix("general ").strip()

        elif decision.startswith("realtime "):
            if realtime_query is None:
                realtime_query = decision.removeprefix("realtime ").strip()

        else:
            # open / close / play / system / content / google search /
            # youtube search / make|create a folder|file
            automation_cmds.append(decision)

    if automation_cmds:
        try:
            asyncio.run(Automation(automation_cmds))
        except Exception:
            traceback.print_exc()

    if general_query:
        answer = ChatBot(general_query)
        Speak(answer)

    if realtime_query:
        answer = RealtimeSearchEngine(realtime_query)
        Speak(answer)

    return True


def main():
    print(f"{Assistantname} is online. Say something, {Username}.")
    running = True
    while running:
        try:
            query = GetQuery()
            if not query:
                continue

            decisions = FirstLayerDMM(query)
            print(f"[Main] Decision: {decisions}")

            running = HandleDecision(decisions)

        except KeyboardInterrupt:
            print("\n[Main] Stopped by user.")
            break
        except Exception:
            print("[Main] Unexpected error, continuing:")
            traceback.print_exc()


if __name__ == "__main__":
    main()