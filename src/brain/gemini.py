from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL

from src.tools.applications import (
    open_application,
    close_application,
)

from src.tools.browser import (
    open_url,
    google_search,
    youtube_search,
)

from src.tools.system import (
    get_current_time,
    get_current_date,
    get_computer_info,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MIRA PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are Mira, a powerful personal AI assistant running on
the user's Mac.

You are:

- Intelligent
- Friendly
- Calm
- Natural
- Helpful
- Concise

The user communicates with you using voice.

Your job is to understand the user's natural language and
use the available tools when the user wants something done
on their Mac.

IMPORTANT RULES:

1. If the user asks you to perform an action, use the
   appropriate tool.

2. Do NOT claim that an action succeeded unless the tool
   reports success.

3. If a tool reports failure, explain the failure naturally.

4. Do not invent tool results.

5. Do not execute arbitrary shell commands.

6. Use the most appropriate tool for the user's request.

7. If the user asks to open an application, use
   open_application.

8. If the user asks to close an application, use
   close_application.

9. If the user asks to open a website, use open_url.

10. If the user asks to search Google, use google_search.

11. If the user asks to search YouTube, use youtube_search.

12. If the user asks for the current time, use
    get_current_time.

13. If the user asks for today's date, use
    get_current_date.

14. If the user asks about the computer, use
    get_computer_info.

15. Keep spoken responses short and natural.

16. Do not use markdown in spoken responses.

17. Do not use emojis.

18. Respond in the same language as the user whenever
    possible.

The user may phrase the same request in many different ways.
Understand the intent instead of looking for exact phrases.
"""


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    open_application,

    close_application,

    open_url,

    google_search,

    youtube_search,

    get_current_time,

    get_current_date,

    get_computer_info,

]


# ============================================================
# GEMINI CHAT
# ============================================================

chat = client.chats.create(

    model=GEMINI_MODEL,

    config=types.GenerateContentConfig(

        system_instruction=SYSTEM_PROMPT,

        tools=TOOLS,

    ),
)


# ============================================================
# ASK MIRA
# ============================================================

def ask_mira(question: str) -> str:
    """
    Send a user request to Gemini.

    Gemini can decide whether it needs to call one of
    Mira's tools.
    """

    try:

        response = chat.send_message(
            question
        )

        if not response.text:

            return (
                "I couldn't generate a response."
            )

        return response.text

    except Exception as error:

        print()
        print(
            "Gemini error:",
            error
        )

        return (
            "Sorry, I couldn't complete "
            "that request."
        )
