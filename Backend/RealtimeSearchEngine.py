import os
import re
import time
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey missing from .env file.")
if not Username or not Assistantname:
    raise ValueError("Username / Assistantname missing from .env file.")

client = Groq(api_key=GroqAPIKey)

DATA_DIR = "Data"
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
MEMORY_PATH = os.path.join(DATA_DIR, "Memory.json")

os.makedirs(DATA_DIR, exist_ok=True)

MAX_HISTORY_PAIRS = 10

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
**  Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.**
**  Always use the facts given to you in the "Permanent Memory" section below when relevant — treat them as ground truth about the user, even if they weren't asked directly in this message.**
**  Always use the live data given to you below (search results and/or stock data) when relevant, and combine them with the Permanent Memory and Real-time Information to give the most complete, accurate answer possible.**
**  Just answer the question from the provided data in a professional way.  **"""

SystemChatBot = [
    {"role": "system", "content": System}
]


def load_chatlog():
    try:
        with open(CHATLOG_PATH, "r") as f:
            return load(f)
    except (FileNotFoundError, ValueError):
        with open(CHATLOG_PATH, "w") as f:
            dump([], f)
        return []

def save_chatlog(msgs):
    with open(CHATLOG_PATH, "w") as f:
        dump(msgs, f, indent=4)

# ---- Permanent memory ----
DEFAULT_MEMORY = {
    "creator": "",
    "user_name": Username,
    "assistant_name": Assistantname,
    "date_of_birth": "",
    "age": "",
    "siblings": {},
    "girlfriend": {},
    "mother": {},
    "father": {},
    "important_facts": [],
    "preferences": []
}

def load_memory():
    try:
        with open(MEMORY_PATH, "r") as f:
            mem = load(f)
        for k, v in DEFAULT_MEMORY.items():
            mem.setdefault(k, v)
        return mem
    except (FileNotFoundError, ValueError):
        with open(MEMORY_PATH, "w") as f:
            dump(DEFAULT_MEMORY, f, indent=4)
        return dict(DEFAULT_MEMORY)

def save_memory(mem):
    with open(MEMORY_PATH, "w") as f:
        dump(mem, f, indent=4)

def update_memory(key, value):
    mem = load_memory()
    mem[key] = value
    save_memory(mem)

def add_fact(fact: str):
    mem = load_memory()
    mem["important_facts"].append(fact)
    save_memory(mem)

def MemoryContext():
    mem = load_memory()
    lines = ["Permanent Memory (facts about the user — always usable):"]
    if mem.get("creator"):
        lines.append(f"- Creator: {mem['creator']}")
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

# ---- Stock price lookup ----
# Common company-name -> ticker aliases, since users say "Apple" not "AAPL"
TICKER_ALIASES = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
    "amazon": "AMZN", "tesla": "TSLA", "meta": "META", "facebook": "META",
    "nvidia": "NVDA", "netflix": "NFLX", "intel": "INTC", "amd": "AMD",
}

STOCK_PATTERN = re.compile(
    r"\b(stock price|share price|stock quote|ticker|share value)\b|\$[A-Za-z]{1,5}\b",
    re.IGNORECASE
)

def extract_ticker(prompt: str):
    """Best-effort: find a known company name or an explicit $TICKER in the prompt."""
    p = prompt.lower()
    for name, ticker in TICKER_ALIASES.items():
        if name in p:
            return ticker
    m = re.search(r"\$([A-Za-z]{1,5})\b", prompt)
    if m:
        return m.group(1).upper()
    return None

def is_stock_query(prompt: str) -> bool:
    return bool(STOCK_PATTERN.search(prompt)) or extract_ticker(prompt) is not None

def GetStockPrice(prompt: str):
    if not YFINANCE_AVAILABLE:
        return "[Stock lookup unavailable: install the 'yfinance' package]"
    ticker_symbol = extract_ticker(prompt)
    if not ticker_symbol:
        return "[Could not determine which company/ticker was meant]"
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        price = info.get("last_price") if hasattr(info, "get") else getattr(info, "last_price", None)
        currency = info.get("currency") if hasattr(info, "get") else getattr(info, "currency", "USD")
        if price is None:
            return f"[No live price found for ticker {ticker_symbol}]"
        return (
            f"Live stock data for {ticker_symbol}:\n"
            f"[start]\n"
            f"Ticker: {ticker_symbol}\n"
            f"Last Price: {price:.2f} {currency}\n"
            f"[end]"
        )
    except Exception as e:
        return f"[Stock lookup failed for {ticker_symbol}: {e}]"

# ---- Web search ----
def GoogleSearch(query, num_results=5, retries=2, delay=2):
    for attempt in range(retries + 1):
        try:
            results = list(search(query, advanced=True, num_results=num_results))
            if not results:
                return f"[No search results found for '{query}']"
            Answer = f"The search results for '{query}' are:\n[start]\n"
            for i in results:
                desc = (i.description or "")[:300]
                Answer += f"Title: {i.title}\nURL: {i.url}\nDescription: {desc}\n\n"
            Answer += "[end]"
            return Answer
        except Exception as e:
            if attempt < retries:
                time.sleep(delay)
                continue
            return f"[Search unavailable: {e}]"

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
    messages = load_chatlog()
    messages.append({"role": "user", "content": prompt})

    if is_stock_query(prompt):
        live_context = GetStockPrice(prompt)
    else:
        live_context = GoogleSearch(prompt)

    system_blocks = [
        {"role": "system", "content": MemoryContext()},
        {"role": "system", "content": Information()},
        {"role": "system", "content": live_context},
    ]

    request_messages = SystemChatBot + system_blocks + messages[-(2 * MAX_HISTORY_PAIRS):]

    Answer = ""
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=request_messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        for chunk in completion:
            choices = getattr(chunk, "choices", None)
            if choices and choices[0].delta and choices[0].delta.content:
                Answer += choices[0].delta.content
    except Exception as e:
        Answer = f"Sorry, I ran into an error talking to the model: {e}"

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    save_chatlog(messages[-(2 * MAX_HISTORY_PAIRS):])

    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query :")
        print(RealtimeSearchEngine(prompt))