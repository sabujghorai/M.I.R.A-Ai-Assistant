import os
import subprocess
import webbrowser
import datetime
import platform
import urllib.parse
import tempfile

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
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.7
recognizer.phrase_threshold = 0.3


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:
    """
    Detect the language/script of the text.

    Returns:
        bn = Bengali
        hi = Hindi
        ru = Russian
        es = Spanish
        en = English
    """

    # Bengali
    for char in text:

        if '\u0980' <= char <= '\u09FF':
            return "bn"

    # Hindi / Devanagari
    for char in text:

        if '\u0900' <= char <= '\u097F':
            return "hi"

    # Russian / Cyrillic
    for char in text:

        if '\u0400' <= char <= '\u04FF':
            return "ru"

    # Basic Spanish word detection
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

    # Default
    return "en"


# ============================================================
# VOICE OUTPUT
# ============================================================

def speak(text: str):
    """
    Speak text using Google Text-to-Speech.

    Supports:
        Bengali
        Hindi
        English
        Russian
        Spanish
    """

    if not text:
        return

    print()
    print("Mallika:", text)

    temp_path = None

    try:

        # Detect response language
        language = detect_language(text)

        print(
            f"Voice language: {language}"
        )

        # Create temporary MP3 file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        )

        temp_path = temp_file.name

        temp_file.close()

        # Generate speech
        tts = gTTS(
            text=text,
            lang=language,
            slow=False
        )

        tts.save(temp_path)

        # Play the generated audio on macOS
        subprocess.run(
            ["afplay", temp_path],
            check=False
        )

    except Exception as e:

        print(
            "Voice error:",
            e
        )

        # Fallback to macOS voice
        try:

            subprocess.run(
                ["say", text],
                check=False
            )

        except Exception as fallback_error:

            print(
                "Fallback voice error:",
                fallback_error
            )

    finally:

        # Delete temporary MP3
        if temp_path:

            try:

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            except Exception:
                pass


# ============================================================
# LISTEN TO USER
# ============================================================

def listen():

    try:

        with sr.Microphone() as source:

            print()
            print("Listening...")

            audio = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=10
            )

    except Exception as e:

        print(
            "Microphone error:",
            e
        )

        return ""


    # Supported languages
    languages = [
        "en-IN",   # English
        "hi-IN",   # Hindi
        "bn-IN",   # Bengali
        "ru-RU",   # Russian
        "es-ES"    # Spanish
    ]


    # Try speech recognition
    for language in languages:

        try:

            text = recognizer.recognize_google(
                audio,
                language=language
            )

            if text:

                print(
                    f"You ({language}): {text}"
                )

                return text


        except sr.UnknownValueError:

            continue


        except sr.RequestError as e:

            print(
                "Speech recognition error:",
                e
            )

            return ""


    print(
        "I couldn't understand what you said."
    )

    return ""


# ============================================================
# MAC APPLICATION CONTROL
# ============================================================

def open_application(app_name: str) -> str:
    """
    Open an installed application on macOS.
    """

    try:

        result = subprocess.run(
            ["open", "-a", app_name],
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
    """
    Close an application on macOS.
    """

    try:

        script = f'''
        tell application "{app_name}"
            quit
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script],
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
    """
    Open a website in the default browser.
    """

    try:

        if not url.startswith(
            ("http://", "https://")
        ):

            url = "https://" + url

        webbrowser.open(url)

        return f"Opened {url}."

    except Exception as e:

        return (
            f"Could not open the website: {e}"
        )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query: str) -> str:
    """
    Search Google for a user query.
    """

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
# YOUTUBE / MUSIC
# ============================================================

def play_song(song: str) -> str:
    """
    Search YouTube for a song or artist.
    """

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
    """
    Get the current local time.
    """

    now = datetime.datetime.now()

    return now.strftime(
        "The current time is %I:%M %p."
    )


# ============================================================
# DATE
# ============================================================

def get_current_date() -> str:
    """
    Get today's date.
    """

    now = datetime.datetime.now()

    return now.strftime(
        "Today is %A, %B %d, %Y."
    )


# ============================================================
# COMPUTER INFORMATION
# ============================================================

def get_computer_info() -> str:
    """
    Get basic Mac information.
    """

    system = platform.system()

    mac_version = platform.mac_ver()[0]

    machine = platform.machine()

    return (
        f"You are using {system}. "
        f"macOS version {mac_version}. "
        f"Machine architecture: {machine}."
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Mallika, a highly capable personal AI assistant
running on the user's Mac.

Your personality:

- Friendly
- Intelligent
- Calm
- Helpful
- Respectful
- Natural
- Conversational

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
8. If the user mixes languages, respond naturally using
   the dominant language.
9. Never translate unless the user asks for translation.


VOICE RULES:

1. Your responses will be spoken aloud.
2. Keep normal responses reasonably short.
3. Do not use markdown.
4. Do not use bullet points unless necessary.
5. Do not use emojis in spoken responses.
6. Sound like a real personal assistant.


COMPUTER CONTROL:

You can use the available tools to control the Mac.

When the user asks you to:

- Open an application → use open_application
- Close an application → use close_application
- Open a website → use open_website
- Search Google → use google_search
- Play/search for music → use play_song
- Ask the current time → use get_current_time
- Ask today's date → use get_current_date
- Ask about the computer → use get_computer_info


IMPORTANT:

Never claim that you performed an action unless the tool
actually reports that it succeeded.

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
            get_computer_info
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

        # Sometimes response.text can be empty
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
# MAIN LOOP
# ============================================================

def main():

    speak(
        " tell me what happen. ? ",
        "what happen ?"
    )

    while True:

        question = listen()

        if not question:
            continue

        command = question.lower().strip()


        # ====================================================
        # TERMINATION COMMANDS
        # ====================================================

        if command in [

            "exit",
            "quit",
            "goodbye",
            "stop",
            "shutdown",

            "just shup up",
            "shut up",

            "terminate",
            "terminate yourself",

            "stop yourself",
            "close yourself",

            "shut yourself down",
            "shutdown yourself",

            "end yourself",
            "end the program",

            "turn yourself off",
            "turn off yourself"

        ]:

            speak(
                "well..!!"
                "take care.."
            )

            break


        # ====================================================
        # OPEN GOOGLE CHROME
        # ====================================================

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

            # IMPORTANT:
            # Do NOT send this command to Gemini.
            continue


        # ====================================================
        # OPEN GOOGLE
        # ====================================================

        if command in [

            "open google",
            "launch google",
            "start google"

        ]:

            result = open_website(
                "https://www.google.com"
            )

            speak(result)

            continue


        # ====================================================
        # OPEN YOUTUBE
        # ====================================================

        if command in [

            "open youtube",
            "launch youtube",
            "start youtube"

        ]:

            result = open_website(
                "https://www.youtube.com"
            )

            speak(result)

            continue


        # ====================================================
        # OPEN SAFARI
        # ====================================================

        if command in [

            "open safari",
            "launch safari",
            "start safari"

        ]:

            result = open_application(
                "Safari"
            )

            speak(result)

            continue


        # ====================================================
        # OPEN FINDER
        # ====================================================

        if command in [

            "open finder",
            "launch finder",
            "start finder"

        ]:

            result = open_application(
                "Finder"
            )

            speak(result)

            continue


        # ====================================================
        # OPEN TERMINAL
        # ====================================================

        if command in [

            "open terminal",
            "launch terminal",
            "start terminal"

        ]:

            result = open_application(
                "Terminal"
            )

            speak(result)

            continue


        # ====================================================
        # OPEN VS CODE
        # ====================================================

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

            continue


        # ====================================================
        # GEMINI AI
        # ====================================================

        answer = ask_mallika(
            question
        )


        # ====================================================
        # SPEAK GEMINI RESPONSE
        # ====================================================

        speak(
            answer
        )

# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()