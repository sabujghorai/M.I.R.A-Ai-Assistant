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
import difflib
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

# Function to perform a google search
def GoogleSearch(Topic):
    search(Topic)  # use pywhatkit's search function to perform a google search
    return True  # Indicate success

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in the default text editor (macOS: TextEdit)
    def OpenNotepad(File):
        subprocess.Popen(["open", "-a", "TextEdit", File])

    # Nested funtion to generate content using AI and save it to a file.
    def ContentWriterAI(Prompt):
        messages.append({"role": "user", "content": f"{Prompt}"})  # Add the user's prompt to message

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_completion_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize the empty string for the response

        # process streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")  # Remove unwanted tkens from the responses
        messages.append({"role": "assistant", "content": Answer})  # Add the AI response to messages
        return Answer

    Topic: str = Topic.replace("Content ", "")  # Remove content from the topic
    ContentByAI = ContentWriterAI(Topic)  # Generated content by AI

    # Save the content to a text file (cross-platform path)
    FilePath = os.path.join(DATA_DIR, f"{Topic.lower().replace(' ', '')}.txt")
    with open(FilePath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)  # Write the content to the file

    OpenNotepad(FilePath)  # Open the file in TextEdit
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

# Function to open an application (macOS) or fall back to a relevant webpage.

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
                    apps.append(entry[:-4])  # strip the .app suffix
    return apps

def resolve_app_name(requested):
    """
    Try to match the requested name against real installed app names.
    Returns the exact installed name if confident, or None if nothing
    installed genuinely matches (meaning: treat this as not installed).
    """
    installed = list_installed_apps()
    requested_clean = requested.strip().lower()

    # 1. Exact match (case-insensitive) — most reliable, always wins.
    for name in installed:
        if name.lower() == requested_clean:
            return name

    # 2. Whole-word containment — "vscode" inside "Visual Studio Code" (as a
    #    word), or "chrome" inside "Google Chrome". This avoids the bug where
    #    "facebook" matched "Books" just because they share the letters
    #    "b-o-o-k" as a raw substring.
    for name in installed:
        name_words = name.lower().split()
        requested_words = requested_clean.split()
        if requested_clean in name_words or name.lower() in requested_words:
            return name

    # 3. Fuzzy match, but with a strict cutoff so partial letter overlap
    #    (like "facebook" vs "books") doesn't false-positive. 0.75 requires
    #    genuinely close spelling, e.g. minor typos.
    matches = difflib.get_close_matches(requested_clean, [n.lower() for n in installed], n=1, cutoff=0.75)
    if matches:
        matched_lower = matches[0]
        for name in installed:
            if name.lower() == matched_lower:
                return name

    return None  # Nothing installed genuinely matches this — not installed.

def is_app_installed(requested):
    """True only if resolve_app_name found a confident match."""
    return resolve_app_name(requested) is not None

def guess_official_domain(app_name, sess, timeout=3):
    """
    Try common domain patterns for a given app/service name (e.g. 'canva' ->
    canva.com, 'notion' -> notion.so) with a real HTTP check, so any app name
    can resolve to a real website automatically — no manual list needed.
    """
    slug = "".join(ch for ch in app_name.strip().lower() if ch.isalnum())
    if not slug:
        return None

    candidates = [
        f"https://www.{slug}.com",
        f"https://{slug}.com",
        f"https://www.{slug}.io",
        f"https://{slug}.io",
        f"https://www.{slug}.app",
        f"https://{slug}.app",
        f"https://www.{slug}.so",
        f"https://{slug}.so",
        f"https://www.{slug}.org",
        f"https://{slug}.org",
        f"https://www.{slug}.net",
        f"https://{slug}.net",
    ]

    headers = {"User-Agent": useragent}
    for url in candidates:
        try:
            resp = sess.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if resp.status_code < 400:
                return resp.url  # use the final URL after any redirects
        except Exception:
            continue
    return None

def OpenApp(app, sess=requests.session()):

    resolved_name = resolve_app_name(app.strip())

    if resolved_name:
        # Genuinely installed — open it locally.
        try:
            result = subprocess.run(["open", "-a", resolved_name], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except Exception:
            pass  # fall through to website logic below if this somehow fails

    # Not installed (or local open failed) — go to the web instead,
    # never guess at a wrong local app.

    # 1. Try common domain patterns first — works for any app name generically,
    #    no manual list to maintain (e.g. "canva" -> canva.com automatically).
    guessed_url = guess_official_domain(app, sess)
    if guessed_url:
        webopen(guessed_url)
        return True

    # 2. Last resort: Google search for the official site, for names that
    #    don't follow a standard domain pattern.
    # Nested function to extract links from the HTML content
    def Extract_links(html):
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')  # parse the html content
        links = soup.find_all('a', {'jsname': 'UKckNb'})  # Find relevent links
        return [link.get('href') for link in links]  # Return the links

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": useragent}  # use the predefined user-agent
        response = sess.get(url, headers=headers)  # perform the get request

        if response.status_code == 200:
            return response.text  # Return the HTML content
        else:
            print("Failed to retrive search results.")  # print an error message
        return None
    html = search_google(f"{app} official website")  # perform the google search

    if html:
        links = Extract_links(html)
        if links:
            webopen(links[0])  # open the first link in the webbrowser

    return True

# Function to close an application (macOS).
def CloseApp(app):

    if "chrome" in app:
        pass
    else:
        try:
            resolved_name = resolve_app_name(app.strip())
            # macOS: ask the app to quit gracefully via AppleScript
            result = subprocess.run(
                ["osascript", "-e", f'quit app "{resolved_name}"'],
                capture_output=True, text=True
            )
            return result.returncode == 0  # Indicate success/failure
        except Exception:
            return False  # Indicate failure
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

    # Execute the appropriate command
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True  # Indicate success

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []  # list to store asynchronous tasks

    for command in commands:
        if command.startswith("open "):  # handle open command

            if "open it" in commands:  # Ignore open it commads
                pass

            if "open file" == command:  # Ignore open file commands.
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))  # schedule app opening
                funcs.append(fun)

        elif command.startswith("general "):  # placeholder for general commands
            pass
        elif command.startswith("realtime "):  # placeholder for real-time commands
            pass
        elif command.startswith("close "):  # handle close commands
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):  # Handle "play" commands
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):  # Handle "content" commands
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):  # Handle "google search" commands
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):  # Handle "youtube search" commands
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):  # Handle "system" commands
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found. for {command}")  # print an error for unrecognized commands

    results = await asyncio.gather(*funcs)  # Execute all task concurrently

    for result in results:  # Process the results
        if isinstance(result, str):
            yield result
        else:
            yield result


# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass

    return True


if __name__ == "__main__":
    asyncio.run(Automation(["open google Chrome","search Github on youtube","play a song on youtube"]))