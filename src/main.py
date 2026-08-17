import os
import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


# Speech recognizer
recognizer = sr.Recognizer()

# Text-to-speech
engine = pyttsx3.init()

engine.setProperty("rate", 180)


def speak(text):
    print("Mallika:", text)
    engine.say(text)
    engine.runAndWait()


def listen():
    with sr.Microphone() as source:

        print("\nListening...")

        audio = recognizer.listen(
            source,
            timeout=None,
            phrase_time_limit=10
        )

    try:
        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You:", text)

        return text

    except sr.UnknownValueError:
        print("I couldn't understand you.")
        return ""

    except sr.RequestError as e:
        print("Speech recognition error:", e)
        return ""

    try:

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You:", text)

        return text

    except sr.UnknownValueError:

        print("I couldn't understand you.")
        return ""

    except sr.RequestError as e:

        print("Speech recognition error:", e)
        return ""


def ask_gemini(question):

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=question
    )

    return response.text


# Main loop
speak("hii sir. how may i help you...?")

while True:

    question = listen()

    if not question:
        continue

    if question.lower() in ["exit", "quit", "goodbye", "stop"]:

        speak("Goodbye.")
        break

    try:

        answer = ask_gemini(question)

        speak(answer)

    except Exception as e:

        print("Gemini error:", e)
        speak("Sorry, I couldn't connect to Gemini.")