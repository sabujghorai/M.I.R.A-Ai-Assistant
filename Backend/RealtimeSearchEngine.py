import os
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey missing from .env file.")

client = Groq(api_key=GroqAPIKey)

DATA_DIR = "Data"
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
MEMORY_PATH = os.path.join(DATA_DIR, "Memory.json")

os.makedirs(DATA_DIR, exist_ok=True)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
**  Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.**
**  Always use the facts given to you in the "Permanent Memory" section below when relevant — treat them as ground truth about the user, even if they weren't asked directly in this message.**
**  Just answer the question from the provided data in a professional way.  **"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# ---- Chat log ----
try:
    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f)

# ---- Permanent memory ----
DEFAULT_MEMORY = {
    "creator": "Sabuj Ghorai",
    "user_name": "Sabuj Ghorai",
    "assistant_name": "Mira",
    "date_of_birth": "2005-05-19",
    "age": "21",
    "siblings": {
        "brother": {"name": "Akash Ghorai", "age": "25"}
    },
    "girlfriend": {"name": "Mallika Bera", "age": "20", "date_of_birth": "2006-02-02"},
    "mother": {"name": "Chameli Ghorai"},
    "father": {"name": "Debendra Ghorai"},
    "important_facts": [],    # freeform list of strings
    "preferences": []
}

def load_memory():
    try:
        with open(MEMORY_PATH, "r") as f:
            mem = load(f)
        for k, v in DEFAULT_MEMORY.items():
            mem.setdefault(k, v)
        return mem
    except FileNotFoundError:
        with open(MEMORY_PATH, "w") as f:
            dump(DEFAULT_MEMORY, f, indent=4)
        return dict(DEFAULT_MEMORY)

def save_memory(mem):
    with open(MEMORY_PATH, "w") as f:
        dump(mem, f, indent=4)

def update_memory(key, value):
    """Simple setter, e.g. update_memory('age', '20')"""
    mem = load_memory()
    mem[key] = value
    save_memory(mem)

def add_fact(fact: str):
    """For anything that doesn't fit a fixed field, e.g. add_fact('Loves chess')"""
    mem = load_memory()
    mem["important_facts"].append(fact)
    save_memory(mem)

def MemoryContext():
    """Formats stored memory into text the model will actually see."""
    mem = load_memory()
    lines = ["Permanent Memory (facts about the user — always usable):"]
    lines.append(f"- Creator: {mem.get('creator')}")
    lines.append(f"- User's name: {mem.get('user_name')}")
    lines.append(f"- Assistant's name: {mem.get('assistant_name')}")
    if mem.get("date_of_birth"):
        lines.append(f"- User's date of birth: {mem['date_of_birth']}")
    if mem.get("age"):
        lines.append(f"- User's age: {mem['age']}")
    for rel, info in mem.get("siblings", {}).items():
        name = info.get("name", "")
        age = info.get("age", "")
        lines.append(f"- {rel.capitalize()}: {name}, age {age}")
    if mem.get("girlfriend"):
        gf = mem["girlfriend"]
        lines.append(f"- Girlfriend: {gf.get('name','')}, age {gf.get('age','')}, DOB {gf.get('date_of_birth','')}")
    if mem.get("mother", {}).get("name"):
        lines.append(f"- Mother: {mem['mother']['name']}")
    if mem.get("father", {}).get("name"):
        lines.append(f"- Father: {mem['father']['name']}")
    for fact in mem.get("important_facts", []):
        lines.append(f"- {fact}")
    for pref in mem.get("preferences", []):
        lines.append(f"- Preference: {pref}")
    return "\n".join(lines)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=3))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        desc = (i.description or "")[:200]
        Answer += f"Title: {i.title}\nDescription: {desc}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def Information():
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(prompt):
    global messages

    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": prompt})
    messages = messages[-10:]

    # Build a FRESH request list each call — never mutate SystemChatBot in place.
    request_messages = (
        SystemChatBot
        + [{"role": "system", "content": MemoryContext()}]
        + [{"role": "system", "content": Information()}]
        + [{"role": "system", "content": GoogleSearch(prompt)}]
        + messages
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=request_messages,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query :")
        print(RealtimeSearchEngine(prompt))