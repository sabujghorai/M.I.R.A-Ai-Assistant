from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "Data"
CHAT_LOG_FILE = DATA_DIR / "ChatLog.json"

env_vard = dotenv_values(ENV_FILE)

Username = env_vard.get("USERNAME")
Assistantname = env_vard.get("ASSISTANT_NAME")
GroqAPIKey = env_vard.get("GROQ_API_KEY")


if not GroqAPIKey:
    raise ValueError(
        f"""
Groq API key is missing.

Make sure your .env file exists here:

{ENV_FILE}

And contains:
USERNAME = Sabuj
ASSISTANT_NAME = MIRA
GroqAPIKey = your_groq_api_key
"""
    )

if not Username:
    Username = "User"


if not Assistantname:
    Assistantname = "Mira"

client = Groq(
    api_key=GroqAPIKey
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

if not CHAT_LOG_FILE.exists():

    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        dump([], f, indent=4)

System = f"""
Hello, I am {Username}. You are {Assistantname}, a very accurate and advanced AI voice assistant.

Your job is to assist {Username} quickly, accurately, and naturally.

Rules:

- Do not tell the current time unless I specifically ask for it.
- Keep your responses short and direct.
- Answer only what I asked.
- Always reply in English, even if I speak Hindi, Bengali, or another language.
- Do not provide unnecessary notes or explanations.
- Never mention your training data.
- Do not repeat the user's question unnecessarily.
- Be polite, helpful, and natural.
- For simple questions, give simple answers.
- For voice responses, avoid unnecessary formatting.
"""

SystemChatBot = [
    {
        "role": "system",
        "content": System
    }
]


def RealtimeInformation():

    current_date_time = datetime.datetime.now()

    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")

    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = "Please use this real-time information if needed.\n"

    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"

    return data

def AnswerModifier(Answer):

    # Split answer into lines
    lines = Answer.split("\n")

    # Remove empty lines
    non_empty_lines = [
        line for line in lines
        if line.strip()
    ]

    # Join lines again
    modified_answer = "\n".join(non_empty_lines)

    return modified_answer.strip()

def ChatBot(Query):

    try:

        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:

            messages = load(f)

        messages.append(
            {
                "role": "user",
                "content": Query
            }
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=(
                SystemChatBot
                +
                [
                    {
                        "role": "system",
                        "content": RealtimeInformation()
                    }
                ]
                +
                messages
            ),
            max_tokens=512,
            temperature=0.5,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                Answer += content

        Answer = Answer.replace("</s>", "").strip()
        messages.append(
            {
                "role": "assistant",
                "content": Answer
            }
        )
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:

            dump(
                messages,
                f,
                indent=4,
                ensure_ascii=False
            )

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"\nError: {e}\n")
        return "Sorry, I encountered an error while processing your request."

if __name__ == "__main__":

    print()
    print("=" * 50)
    print(f"{Assistantname} AI Assistant")
    print("=" * 50)
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.lower() in [
            "exit",
            "quit",
            "terminate yourself"
        ]:
            print(f"{Assistantname}: Goodbye!")
            break
        response = ChatBot(user_input)
        print(f"{Assistantname}: {response}")