# Imported the requered libraries
from webbrowser import open as webopen  # Import webbrowser functionalities
from pywhatkit import search, playonyt  # Import functios for google search and youube playback
from dotenv import dotenv_values  # Import dotenv to manage enviornment variables.
from bs4 import BeautifulSoup  # Import Beautifulsoup for parsing HTML content
from rich import print  # Import rich for styled consile output
from groq import Groq  # import groq for AI chat functionalities
import webbrowser
import subprocess
import requests
import asyncio
import concurrent.futures
import difflib
import re
import os

# Load Enviornment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")  # fixed: was os.environ['Username'], which isn't set by dotenv_values

# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "zZcWbf",
    "hgKElc",
    "LTKOO sY7ric",
    "z0Lcw",
    "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc",
    "O5uR6d LTKOO",
    "vlzY6d",
    "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt",
    "sXLaOe",
    "LwkfKe",
    "VQF4g",
    "qv3Wpe",
    "kno-rdesc",
    "SPZz6b"
]

# Define a user-agent for making web requests.
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc"}]

# Data directory setup (cross-platform)
DATA_DIR = os.path.join(os.getcwd(), "Data")
os.makedirs(DATA_DIR, exist_ok=True)

# Function to create a folder, a file, or a file inside a folder (creates missing parent folders automatically)
def CreateFileOrFolder(path, is_file=False, content=""):
    if is_file:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    else:
        os.makedirs(path, exist_ok=True)

    return True

# Common shorthand locations mapped to their real macOS paths.
COMMON_LOCATIONS = {
    "desktop": os.path.expanduser("~/Desktop"),
    "documents": os.path.expanduser("~/Documents"),
    "downloads": os.path.expanduser("~/Downloads"),
    "pictures": os.path.expanduser("~/Pictures"),
    "music": os.path.expanduser("~/Music"),
    "movies": os.path.expanduser("~/Movies"),
    "home": os.path.expanduser("~"),
    "data": DATA_DIR,
}

def resolve_location(location_text):
    location_text = location_text.strip().lower()
    location_text = re.sub(r"^(the|my|inside|in|on)\s+", "", location_text).strip()

    parts = re.split(r"[\\/]", location_text)
    first = parts[0].strip()

    if first in COMMON_LOCATIONS:
        base = COMMON_LOCATIONS[first]
        remainder = parts[1:]
        return os.path.join(base, *remainder) if remainder else base

    return os.path.expanduser(os.path.join("~", location_text))

def CreateFromCommand(command):
    command = command.strip().lower()

    is_file = bool(re.search(r"\bfile\b", command))

    name_match = re.search(r"(?:called|named)\s+([^\s]+(?:\s+[^\s]+)*?)\s+(?:inside|in|on)\b", command)
    if not name_match:
        name_match = re.search(r"(?:folder|file)\s+([^\s]+)\s+(?:inside|in|on)\b", command)

    location_match = re.search(r"(?:inside|in|on)\s+(.+)$", command)

    if not name_match or not location_match:
        print("Sorry, I couldn't understand the folder/file name or location from that command.")
        return False

    name = name_match.group(1).strip()
    location_text = location_match.group(1).strip()
    base_path = resolve_location(location_text)

    full_path = os.path.join(base_path, name)

    if is_file:
        CreateFileOrFolder(full_path, is_file=True)
    else:
        CreateFileOrFolder(full_path, is_file=False)

    return True

# Function to perform a google search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save it to a file.
def Content(Topic):

    def OpenNotepad(File):
        subprocess.Popen(["open", "-a", "TextEdit", File])

    def ContentWriterAI(Prompt):
        messages.append({"role": "user", "content": f"{Prompt}"})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_completion_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    FilePath = os.path.join(DATA_DIR, f"{Topic.lower().replace(' ', '')}.txt")
    with open(FilePath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(FilePath)
    return True

# Function to search content in you tube
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query)
    return True

# Directories macOS installs .app bundles into — scanned to build the real app list.
APP_DIRS = [
    "/Applications",
    "/System/Applications",
    "/System/Applications/Utilities",
    os.path.expanduser("~/Applications"),
]

def list_installed_apps():
    """Return the exact names (as macOS sees them) of all installed .app bundles."""
    apps = []
    for d in APP_DIRS:
        if os.path.isdir(d):
            for entry in os.listdir(d):
                if entry.endswith(".app"):
                    apps.append(entry[:-4])
    return apps

def resolve_app_name(requested):
    """
    Typo-tolerant matching against installed app names.
    Handles missing letters, extra letters, swapped letters, partial typing, etc.
    Returns the exact installed app name if a confident match is found, else None.
    """
    installed = list_installed_apps()
    if not installed:
        return None

    requested_clean = requested.strip().lower()
    requested_clean = re.sub(r"[^a-z0-9 ]", "", requested_clean)  # strip punctuation

    if not requested_clean:
        return None

    # 1. Exact match (case-insensitive) — always wins first.
    for name in installed:
        if name.lower() == requested_clean:
            return name

    # 2. Substring match either direction — catches typing "docker" when app
    #    is "Docker Desktop", or typing part of a longer name.
    for name in installed:
        name_lower = name.lower()
        if requested_clean in name_lower or name_lower in requested_clean:
            return name

    # 3. Fuzzy match against FULL installed names, generous cutoff.
    #    Handles missing/extra/swapped letters like "docke", "ocker", "dcoker".
    lowered_map = {n.lower(): n for n in installed}
    matches = difflib.get_close_matches(requested_clean, lowered_map.keys(), n=1, cutoff=0.55)
    if matches:
        return lowered_map[matches[0]]

    # 4. Fuzzy match against the FIRST WORD of each installed app too —
    #    e.g. requested "docke" vs "Docker" as the first word of "Docker Desktop".
    first_word_map = {}
    for name in installed:
        first_word = name.lower().split()[0] if name.split() else name.lower()
        first_word_map.setdefault(first_word, name)

    matches = difflib.get_close_matches(requested_clean, first_word_map.keys(), n=1, cutoff=0.55)
    if matches:
        return first_word_map[matches[0]]

    return None  # genuinely nothing close enough — not installed

def is_app_installed(requested):
    """True only if resolve_app_name found a confident match."""
    return resolve_app_name(requested) is not None

def guess_official_domain(app_name, sess, timeout=1.5):
    """
    Try common domain patterns for a given app/service name (e.g. 'canva' ->
    canva.com) with real HTTP checks run IN PARALLEL and a short timeout,
    so this returns fast instead of testing many URLs one at a time.
    """
    slug = "".join(ch for ch in app_name.strip().lower() if ch.isalnum())
    if not slug:
        return None

    candidates = [
        f"https://{slug}.com",
        f"https://www.{slug}.com",
        f"https://{slug}.io",
        f"https://{slug}.so",
    ]

    headers = {"User-Agent": useragent}

    def check(url):
        try:
            resp = sess.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if resp.status_code < 400:
                return resp.url
        except Exception:
            return None
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidates)) as executor:
        for result in executor.map(check, candidates):
            if result:
                return result
    return None

# Famous apps mapped straight to their real websites — skips slow domain-guessing/network calls
KNOWN_APP_WEBSITES = {
    "docker": "https://www.docker.com",
    "kubernetes": "https://kubernetes.io",
    "facebook": "https://www.facebook.com/",
    "chrome": "https://www.google.com/chrome",
    "google chrome": "https://www.google.com/chrome",
    "notion": "https://www.notion.so",
    "canva": "https://www.canva.com",
    "app store": "https://www.apple.com/app-store",
    "system setting": "https://support.apple.com/guide/mac-help/change-system-settings-mchlp2865/mac",
    "setting": "https://support.apple.com/guide/mac-help/change-system-settings-mchlp2865/mac",
    "maps": "https://www.apple.com/maps",
    "vscode": "https://code.visualstudio.com",
    "visual studio code": "https://code.visualstudio.com",
    "slack": "https://slack.com",
    "spotify": "https://www.spotify.com",
    "zoom": "https://zoom.us",
}

def OpenApp(app, sess=requests.session()):
    """
    Opens one or multiple applications, typo-tolerant, e.g. "docke, chrme and kubernets".
    - If an app is installed (even if misspelled), it opens locally.
    - If it's genuinely not installed, it opens that app's official website instead
      (known dictionary first, then a guessed domain, then a Google search as last resort).
    Runs all apps concurrently for speed.
    """

    def open_one(single_app):
        single_app = single_app.strip()
        if not single_app:
            return True

        resolved_name = resolve_app_name(single_app)

        if resolved_name:
            try:
                result = subprocess.run(
                    ["open", "-a", resolved_name],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    print(f"[OpenApp] Opened '{resolved_name}' (you typed '{single_app}')")
                    return True
                else:
                    print(f"[OpenApp] Found '{resolved_name}' but couldn't open it: {result.stderr.strip()}")
            except Exception as e:
                print(f"[OpenApp] Error opening '{resolved_name}': {e}")

        # Not installed — go to the web.
        key = single_app.lower().rstrip("s")
        for dict_key, url in KNOWN_APP_WEBSITES.items():
            if dict_key.rstrip("s") == key:
                webopen(url)
                print(f"[OpenApp] '{single_app}' not installed — opened known site {url}")
                return True

        guessed_url = guess_official_domain(single_app, sess)
        if guessed_url:
            webopen(guessed_url)
            print(f"[OpenApp] '{single_app}' not installed — opened guessed site {guessed_url}")
            return True

        query = single_app.replace(" ", "+")
        webopen(f"https://www.google.com/search?q={query}+official+website")
        print(f"[OpenApp] '{single_app}' not installed — opened Google search")
        return True

    cleaned = re.sub(r"^\s*open\s+", "", app.strip(), flags=re.IGNORECASE)
    app_names = re.split(r"\s*(?:,|&|\band\b)\s*", cleaned, flags=re.IGNORECASE)
    app_names = [name.strip() for name in app_names if name.strip()]

    if not app_names:
        return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(app_names)) as executor:
        results = list(executor.map(open_one, app_names))

    return all(results)

# Function to close an application (macOS). Supports multiple apps in one command.
def CloseApp(app):
    app_names = re.split(r"\s*(?:,|&|\band\b)\s*", app.strip(), flags=re.IGNORECASE)
    app_names = [name.strip() for name in app_names if name.strip()]

    overall_success = True

    for single_app in app_names:
        if "chrome" in single_app.lower():
            continue
        else:
            try:
                resolved_name = resolve_app_name(single_app.strip())
                if not resolved_name:
                    overall_success = False
                    continue
                result = subprocess.run(
                    ["osascript", "-e", f'quit app "{resolved_name}"'],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    overall_success = False
            except Exception:
                overall_success = False

    return overall_success

# Function to execute system-level commands (macOS volume control via osascript).
def System(command):

    def mute():
        subprocess.run(["osascript", "-e", "set volume with output muted"])

    def unmute():
        subprocess.run(["osascript", "-e", "set volume without output muted"])

    def volume_up():
        subprocess.run([
            "osascript", "-e",
            "set volume output volume ((output volume of (get volume settings)) + 10)"
        ])

    def volume_down():
        subprocess.run([
            "osascript", "-e",
            "set volume output volume ((output volume of (get volume settings)) - 10)"
        ])

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):

            if "open it" in commands:
                pass

            if "open file" == command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        elif command.startswith("make a folder") or command.startswith("create a folder") \
                or command.startswith("make a file") or command.startswith("create a file"):
            fun = asyncio.to_thread(CreateFromCommand, command)
            funcs.append(fun)

        else:
            print(f"No Function Found. for {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass

    return True