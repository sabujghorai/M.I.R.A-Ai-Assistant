# This is the Brain Of MY AI

import cohere
from rich import print
from dotenv import dotenv_values

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve the API key
CohereAPIKey = env_vars["CohereAPIKey"]

# create a cohere client using the provided api key
co = cohere.Client(api_key=CohereAPIKey)

# Defined a list of recognized function keywords for task recognition
funcs = [
    "exit", "general", "realtime", "open", "close", "play", "pause",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Initialized an empty list to store the running conversation (currently unused
# by the API call below, but kept here in case you want to extend chat_history
# with real conversation turns later).
message = []

# define the preamble that guides the ai model on how to categorize the queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform
a task.

*** Do not answer any query, just decide what kind of query is given to you. ***

→ Respond with 'general (query)' if a query can be answered by a llm model (conversational ai)
  and does NOT require any up-to-date, personal, or external information — e.g. well-known,
  unchanging facts, casual conversation, opinions, or general knowledge.
→ Respond with 'realtime (query)' if a query requires up-to-date, current, or specific factual
  information that a language model trained on past data cannot reliably know — including
  questions about real people (public figures or private individuals), current events, news,
  prices, weather, sports scores, or anything time-sensitive.
→ Respond with 'open (application name or website name)' if a query is asking to open any application or website.
→ Respond with 'close (application name)' if a query is asking to close any application like 'close chrome'.
→ Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys'.
→ Respond with 'generate image (image prompt)' if a query is requesting to generate an image with a prompt.
→ Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder.
→ Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, etc.
→ Respond with 'content (topic)' if a query is asking to write any type of content like applications, emails, etc.
→ Respond with 'google search (topic)' if a query is asking to search a specific topic on Google.
→ Respond with 'youtube search (topic)' if a query is asking to search a specific topic on YouTube.

*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp',
respond with multiple classifications separated appropriately. ***

*** If the user is saying goodbye or wants to end the conversation, like 'bye', 'goodbye',
or 'bye EV', 'terminate yourself', 'quit yourself', 'stop talking', 'just go ahed', 'shut up','i don't want to see again','fuck offjust ','go to hell','please stop','stop the conversation','shutdown','shutdown yourself','sleep' respond with 'exit (query)' ***

*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to
have a normal conversation. ***
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    # --- new examples to teach the model when to classify as 'realtime' ---
    {"role": "User", "message": "who is Elon Musk"},
    {"role": "Chatbot", "message": "realtime who is Elon Musk"},
    {"role": "User", "message": "who is Sabuj Ghorai"},
    {"role": "Chatbot", "message": "realtime who is Sabuj Ghorai"},
    {"role": "User", "message": "what is the capital of France"},
    {"role": "Chatbot", "message": "general what is the capital of France"},
    {"role": "User", "message": "what's the weather like today"},
    {"role": "Chatbot", "message": "realtime what's the weather like today"},
    {"role": "User", "message": "who won the cricket match yesterday"},
    {"role": "Chatbot", "message": "realtime who won the cricket match yesterday"},
    # --- new examples to teach the model when to classify as 'exit' ---
    {"role": "User", "message": "bye"},
    {"role": "Chatbot", "message": "exit bye"},
    {"role": "User", "message": "goodbye"},
    {"role": "Chatbot", "message": "exit goodbye"},
    {"role": "User", "message": "bye jarvis"},
    {"role": "Chatbot", "message": "exit bye jarvis"},
]

def FirstLayerDMM(prompt: str = "test"):
    """Classify a user query into one or more task categories."""

    # keep a running record of what the user has said (available for future use)
    message.append({"role": "user", "content": f"{prompt}"})

    # create a streaming chat session with the cohere model
    stream = co.chat_stream(
        model="command-a-03-2025",   # currently supported Cohere chat model
        message=prompt,              # pass the user's query
        temperature=0.7,             # creativity level of the model
        chat_history=ChatHistory,    # few-shot examples for classification
        prompt_truncation="OFF",
        connectors=[],
        preamble=preamble
    )

    response = ""

    for event in stream:
        if event.event_type == "text-generation":
            response += event.text  # append generated text to the response

    response = response.replace("\n", "")
    response = response.split(",")
    response = [i.strip() for i in response]

    temp = []

    # filter the tasks based on recognized function keywords
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
                break  # avoid matching the same task against multiple funcs

    response = temp

    # if the model couldn't confidently classify (raw "(query)" leftover), retry once
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response


if __name__ == "__main__":
    while True:
        result = FirstLayerDMM(input(">>> "))
        print(result)
        if any(r.startswith("exit") for r in result):
            print("Have a Good Day !")
            break