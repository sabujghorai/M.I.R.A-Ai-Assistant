import os
import subprocess
import time
import webbrowser
import datetime
import platform
import urllib.parse
import tempfile
import re

import speech_recognition as sr

from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3-flash-preview"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ACTIVATION_SOUND = os.path.join(
    BASE_DIR,
    "sounds",
    "siri-sound-effect.mp3"
)


# ============================================================
# SETTINGS
# ============================================================

WAKE_WORDS = [
    "hey ms",
    "hey miss",
    "hey ems",
    "hey m s",
    "hey mess",
    "ms",
    "miss",
    "ems",
    "m s",
    "mess"
]

SLEEP_COMMANDS = [
    "go to sleep",
    "sleep",
    "stop listening",
    "stop listening mallika",
    "that's all",
    "thats all",
    "thank you mallika",
    "thank you",
    "thanks mallika"
]

EXIT_COMMANDS = [
    "exit",
    "quit",
    "goodbye",
    "shutdown",
    "terminate",
    "terminate yourself",
    "end the program",
    "turn yourself off",
    "turn off yourself"
]


# ============================================================
# ACTIVATION SOUND
# ============================================================

def play_activation_sound():
    """
    Play the activation sound using macOS afplay.
    """

    try:

        if not os.path.exists(ACTIVATION_SOUND):

            print(
                f"Activation sound not found: "
                f"{ACTIVATION_SOUND}"
            )

            return

        subprocess.Popen(
            [
                "afplay",
                ACTIVATION_SOUND
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:

        print(
            "Activation sound error:",
            e
        )


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.7
recognizer.phrase_threshold = 0.3


# ============================================================
# MICROPHONE CALIBRATION
# ============================================================

def calibrate_microphone():

    try:

        with sr.Microphone() as source:

            print("Calibrating microphone...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            print("Microphone ready.")

    except Exception as e:

        print(
            "Microphone calibration error:",
            e
        )


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:

    # Bengali
    for char in text:

        if '\u0980' <= char <= '\u09FF':
            return "bn"

    # Hindi
    for char in text:

        if '\u0900' <= char <= '\u097F':
            return "hi"

    # Russian
    for char in text:

        if '\u0400' <= char <= '\u04FF':
            return "ru"

    # Spanish
    lower_text = text.lower()

    spanish_words = [
        "hola",
        "gracias",
        "buenos",
        "buenas",
        "cómo",
        "como",
        "estás",
        "esta",
        "qué",
        "que",
        "por favor",
        "adiós",
        "adios"
    ]

    for word in spanish_words:

        if word in lower_text:
            return "es"

    return "en"


# ============================================================
# VOICE OUTPUT
# ============================================================

def speak(text: str):

    if not text:
        return

    print()
    print("Mallika:", text)

    temp_path = None

    try:

        language = detect_language(text)

        print(
            f"Voice language: {language}"
        )

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        )

        temp_path = temp_file.name

        temp_file.close()

        tts = gTTS(
            text=text,
            lang=language,
            slow=False
        )

        tts.save(temp_path)

        subprocess.run(
            [
                "afplay",
                temp_path
            ],
            check=False
        )

    except Exception as e:

        print(
            "Voice error:",
            e
        )

        try:

            subprocess.run(
                [
                    "say",
                    text
                ],
                check=False
            )

        except Exception as fallback_error:

            print(
                "Fallback voice error:",
                fallback_error
            )

    finally:

        if temp_path:

            try:

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            except Exception:
                pass


# ============================================================
# SPEECH RECOGNITION HELPER
# ============================================================

def recognize_audio(audio):

    languages = [
        "en-IN",
        "hi-IN",
        "bn-IN",
        "ru-RU",
        "es-ES"
    ]

    for language in languages:

        try:

            text = recognizer.recognize_google(
                audio,
                language=language
            )

            if text:

                return text.strip()

        except sr.UnknownValueError:

            continue

        except sr.RequestError as e:

            print(
                "Speech recognition error:",
                e
            )

            return ""

    return ""


# ============================================================
# WAIT FOR WAKE WORD
# ============================================================

def wait_for_wake_word():

    while True:

        try:

            with sr.Microphone() as source:

                print()
                print(
                    "Waiting for "
                    "\"Hey MS\"..."
                )

                try:

                    audio = recognizer.listen(
                        source,
                        timeout=None,
                        phrase_time_limit=5
                    )

                except Exception:

                    continue

            text = recognize_audio(audio)

            if not text:
                continue

            text_lower = text.lower().strip()

            print(
                f"Heard: {text}"
            )

            # ------------------------------------------------
            # Find wake word
            # ------------------------------------------------

            for wake_word in WAKE_WORDS:

                if wake_word in text_lower:

                    print(
                        "Wake word detected!"
                    )

                    # Remove wake word
                    command = re.sub(
                        re.escape(wake_word),
                        "",
                        text,
                        count=1,
                        flags=re.IGNORECASE
                    ).strip(
                        " ,.!?"
                    )

                    return command

        except Exception as e:

            print(
                "Wake-word error:",
                e
            )

            time.sleep(0.5)


# ============================================================
# LISTEN FOR COMMAND
# ============================================================

def listen_command():

    try:

        with sr.Microphone() as source:

            print()
            print("Listening...")

            try:

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            except sr.WaitTimeoutError:

                return ""

        text = recognize_audio(audio)

        if text:

            print(
                f"You: {text}"
            )

            return text

        print(
            "I couldn't understand what you said."
        )

        return ""

    except Exception as e:

        print(
            "Microphone error:",
            e
        )

        return ""


# ============================================================
# MAC APPLICATION CONTROL
# ============================================================

def open_application(app_name: str) -> str:

    try:

        result = subprocess.run(
            [
                "open",
                "-a",
                app_name
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            return (
                f"Successfully opened "
                f"{app_name}."
            )

        return (
            f"I couldn't open {app_name}. "
            f"Please check whether the application "
            f"is installed."
        )

    except Exception as e:

        return (
            f"Could not open {app_name}: {e}"
        )


def close_application(app_name: str) -> str:

    try:

        script = f'''
        tell application "{app_name}"
            quit
        end tell
        '''

        result = subprocess.run(
            [
                "osascript",
                "-e",
                script
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            return (
                f"Successfully closed "
                f"{app_name}."
            )

        return (
            f"I couldn't close {app_name}."
        )

    except Exception as e:

        return (
            f"Could not close {app_name}: {e}"
        )


# ============================================================
# WEBSITE CONTROL
# ============================================================

def open_website(url: str) -> str:

    try:

        if not url.startswith(
            (
                "http://",
                "https://"
            )
        ):

            url = "https://" + url

        webbrowser.open(url)

        return (
            "Successfully opened the website."
        )

    except Exception as e:

        return (
            f"Could not open the website: {e}"
        )


# ============================================================
# GOOGLE
# ============================================================

def google_search(query: str) -> str:

    try:

        encoded_query = urllib.parse.quote_plus(
            query
        )

        url = (
            "https://www.google.com/search?q="
            + encoded_query
        )

        webbrowser.open(url)

        return (
            f"I searched Google for "
            f"{query}."
        )

    except Exception as e:

        return (
            f"Google search failed: {e}"
        )


# ============================================================
# YOUTUBE
# ============================================================

def play_song(song: str) -> str:

    try:

        encoded_song = urllib.parse.quote_plus(
            song
        )

        url = (
            "https://www.youtube.com/results?search_query="
            + encoded_song
        )

        webbrowser.open(url)

        return (
            f"I opened YouTube and searched "
            f"for {song}."
        )

    except Exception as e:

        return (
            f"I couldn't search for "
            f"{song}: {e}"
        )


# ============================================================
# TIME
# ============================================================

def get_current_time() -> str:

    now = datetime.datetime.now()

    return now.strftime(
        "The current time is %I:%M %p."
    )


# ============================================================
# DATE
# ============================================================

def get_current_date() -> str:

    now = datetime.datetime.now()

    return now.strftime(
        "Today is %A, %B %d, %Y."
    )


# ============================================================
# COMPUTER INFORMATION
# ============================================================

def get_computer_info() -> str:

    system = platform.system()

    mac_version = platform.mac_ver()[0]

    machine = platform.machine()

    return (
        f"You are using {system}. "
        f"macOS version {mac_version}. "
        f"Machine architecture: {machine}."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression: str) -> str:

    """
    Safe basic calculator.

    Supports:
        + - * / % ** ( )
    """

    try:

        expression = expression.lower()

        expression = expression.replace(
            "calculate",
            ""
        )

        expression = expression.replace(
            "what is",
            ""
        )

        expression = expression.strip()

        # Only allow mathematical characters
        if not re.fullmatch(
            r"[0-9+\-*/().%\s]+",
            expression
        ):

            return (
                "I can only calculate "
                "basic mathematical expressions."
            )

        result = eval(
            expression,
            {
                "__builtins__": None
            },
            {}
        )

        return f"The answer is {result}."

    except Exception:

        return (
            "I couldn't calculate that."
        )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Mallika, a highly capable personal AI assistant
running on the user's Mac.

Your personality:

Friendly, intelligent, calm, helpful, respectful,
natural and conversational.

You communicate in:

1. English
2. Hindi
3. Bengali
4. Russian
5. Spanish

LANGUAGE RULES:

1. Detect the language used by the user.
2. Respond in the same language.
3. If the user speaks Bengali, answer in Bengali.
4. If the user speaks Hindi, answer in Hindi.
5. If the user speaks Russian, answer in Russian.
6. If the user speaks Spanish, answer in Spanish.
7. If the user speaks English, answer in English.

VOICE RULES:

1. Your responses will be spoken aloud.
2. Keep normal responses reasonably short.
3. Do not use markdown.
4. Do not use emojis in spoken responses.
5. Sound like a real personal assistant.

COMPUTER CONTROL:

When the user asks you to:

- Open an application → use open_application
- Close an application → use close_application
- Open a website → use open_website
- Search Google → use google_search
- Search/play music → use play_song
- Ask current time → use get_current_time
- Ask today's date → use get_current_date
- Ask about computer → use get_computer_info
- Calculate something → use calculate

IMPORTANT:

Never claim that an action succeeded unless the tool
actually reports success.

Do not invent tool results.

Do not execute arbitrary shell commands.

You are Mallika, the user's personal AI assistant.
"""


# ============================================================
# GEMINI CHAT
# ============================================================

chat = client.chats.create(

    model=MODEL,

    config=types.GenerateContentConfig(

        system_instruction=SYSTEM_PROMPT,

        tools=[
            open_application,
            close_application,
            open_website,
            google_search,
            play_song,
            get_current_time,
            get_current_date,
            get_computer_info,
            calculate
        ]
    )
)


# ============================================================
# ASK MALLIKA
# ============================================================

def ask_mallika(question: str) -> str:

    try:

        response = chat.send_message(
            question
        )

        if not response.text:

            return (
                "I didn't receive a response."
            )

        return response.text

    except Exception as e:

        print()
        print(
            "Gemini error:",
            e
        )

        return (
            "Sorry, I couldn't complete "
            "that request."
        )


# ============================================================
# HANDLE COMMAND
# ============================================================

def handle_command(question: str):

    command = question.lower().strip()

    # ========================================================
    # EXIT
    # ========================================================

    if command in EXIT_COMMANDS:

        speak(
            "Goodbye. Take care."
        )

        return "EXIT"


    # ========================================================
    # SLEEP / STOP LISTENING
    # ========================================================

    if command in SLEEP_COMMANDS:

        speak(
            "Okay. I'm listening for you."
        )

        return "SLEEP"


    # ========================================================
    # OPEN CHROME
    # ========================================================

    if command in [

        "open google chrome",
        "open chrome",
        "launch google chrome",
        "launch chrome",
        "start google chrome",
        "start chrome"

    ]:

        result = open_application(
            "Google Chrome"
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # OPEN GOOGLE
    # ========================================================

    if command in [

        "open google",
        "launch google",
        "start google"

    ]:

        open_website(
            "https://www.google.com"
        )

        speak(
            "Successfully opened Google."
        )

        return "CONTINUE"


    # ========================================================
    # OPEN YOUTUBE
    # ========================================================

    if command in [

        "open youtube",
        "launch youtube",
        "start youtube"

    ]:

        open_website(
            "https://www.youtube.com"
        )

        speak(
            "Successfully opened YouTube."
        )

        return "CONTINUE"


    # ========================================================
    # OPEN SAFARI
    # ========================================================

    if command in [

        "open safari",
        "launch safari",
        "start safari"

    ]:

        result = open_application(
            "Safari"
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # OPEN FINDER
    # ========================================================

    if command in [

        "open finder",
        "launch finder",
        "start finder"

    ]:

        result = open_application(
            "Finder"
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # OPEN TERMINAL
    # ========================================================

    if command in [

        "open terminal",
        "launch terminal",
        "start terminal"

    ]:

        result = open_application(
            "Terminal"
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # OPEN VS CODE
    # ========================================================

    if command in [

        "open visual studio code",
        "open vs code",
        "open vscode",
        "launch visual studio code",
        "launch vs code",
        "start visual studio code",
        "start vs code"

    ]:

        result = open_application(
            "Visual Studio Code"
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # CALCULATOR
    # ========================================================

    calculator_pattern = re.fullmatch(
        r"(calculate|what is)\s+"
        r"[0-9+\-*/().%\s]+",
        command
    )

    if calculator_pattern:

        result = calculate(
            command
        )

        speak(result)

        return "CONTINUE"


    # ========================================================
    # GEMINI
    # ========================================================

    answer = ask_mallika(
        question
    )

    speak(answer)

    return "CONTINUE"


# ============================================================
# ACTIVE CONVERSATION
# ============================================================

def active_conversation(first_command=""):

    """
    After the wake word is detected, Mallika stays active.

    Example:

        Hey MS, open Google
        Open YouTube
        What time is it?
        Calculate 25 * 4
        Go to sleep

    The user does NOT need to say "Hey MS" before every command.
    """

    # --------------------------------------------------------
    # First command may already be attached to wake word
    # --------------------------------------------------------

    if first_command:

        result = handle_command(
            first_command
        )

        if result == "EXIT":
            return "EXIT"

        if result == "SLEEP":
            return "SLEEP"


    # --------------------------------------------------------
    # Continue conversation
    # --------------------------------------------------------

    while True:

        question = listen_command()

        # No speech detected
        if not question:

            print(
                "No command detected."
            )

            return "SLEEP"

        result = handle_command(
            question
        )

        if result == "EXIT":

            return "EXIT"

        if result == "SLEEP":

            return "SLEEP"


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=========================================="
    )
    print(
        "        MALLIKA AI ASSISTANT"
    )
    print(
        "=========================================="
    )

    print()
    print(
        "Say \"Hey MS\" to activate Mallika."
    )

    # --------------------------------------------------------
    # Calibrate microphone once
    # --------------------------------------------------------

    calibrate_microphone()

    # --------------------------------------------------------
    # Startup activation sound
    # --------------------------------------------------------

    play_activation_sound()

    # --------------------------------------------------------
    # MAIN WAKE-WORD LOOP
    # --------------------------------------------------------

    while True:

        # Wait for:
        # Hey MS
        # MS
        # Hey Miss
        # etc.

        first_command = wait_for_wake_word()

        # ----------------------------------------------------
        # Wake word detected
        # ----------------------------------------------------

        play_activation_sound()

        print()
        print(
            "Mallika activated."
        )

        # ----------------------------------------------------
        # Stay active and process commands
        # ----------------------------------------------------

        result = active_conversation(
            first_command
        )

        # ----------------------------------------------------
        # Completely exit program
        # ----------------------------------------------------

        if result == "EXIT":

            break

        # ----------------------------------------------------
        # Otherwise return to wake-word mode
        # ----------------------------------------------------

        print()
        print(
            "Mallika is sleeping."
        )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()