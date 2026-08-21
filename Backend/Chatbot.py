from groq import Groq # importing the groq library to use the API  
from json import load,dump # importing function to read and write the json file
import datetime # for real time date and time information
from dotenv import dotenv_values # importing the dotenv_values to read enviornment variables from a .env file


env_vard = dotenv_values(".env")

# Retrive specific envirenment variables for username,assistant name and API keys
Username = env_vard.get("Username")
Assistantname = env_vard.get("Assistantname")
GroqAPIKey = env_vard.get("GroqAPIKey")

# initializing the Groq client using the provided API key
client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""
Hello, I am {Username}. You are {Assistantname}, a highly accurate, advanced, intelligent, and natural AI voice assistant.

Your primary goal is to assist {Username} quickly, accurately, naturally, and helpfully.

Rules:

- Always understand what {Username} is asking and answer the actual request directly.
- If {Username} asks for the current time, tell the current time accurately. Understand natural time-related questions such as:
  "What time is it?", "Tell me the time", "What's the time now?", "Abhi kitne baje hain?", "এখন কয়টা বাজে?", etc.
- Respond in the same language that {Username} is using.
- If {Username} speaks Hindi, respond in Hindi.
- If {Username} speaks Bengali, respond in Bengali.
- If {Username} speaks English, respond in English.
- If {Username} mixes languages, respond naturally using the same language mix when appropriate.
- Keep responses concise and direct unless {Username} asks for a detailed explanation.
- Do not provide unnecessary information, notes, warnings, or explanations.
- Be polite, friendly, helpful, confident, and natural.
- Support {Username}'s decisions and goals whenever possible.
- Follow {Username}'s instructions and try to complete requested tasks whenever technically possible.
- If a task requires information, tools, or permissions that you do not have, clearly explain the limitation instead of pretending that you completed it.
- Never claim that you performed an action unless you actually performed it.
- You should tell the accurate time, weather.
- Never mention your training data or knowledge cutoff.
- Remember the context of the current conversation and use it when answering.
- Prioritize accuracy, usefulness, and natural conversation.
- When {Username} gives a simple command, execute it or provide the direct answer without unnecessary conversation.
"""

# A list of instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Attempt to load the chat log from a json file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([],f)

# function to get real-time data and time information
def RealtimeInformation():
    current_data_time = datetime.datetime.now() # get the current data and time
    day = current_data_time.strftime("%A") # Day of the week
    date = current_data_time.strftime("%d")
    month = current_data_time.strftime("%B")
    year = current_data_time.strftime("%Y")
    hour = current_data_time.strftime("%H")
    minute = current_data_time.strftime("%M")
    second = current_data_time.strftime("%S")

    # format the information into a string.
    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nyear: {year}\n"
    date += f"Time: {hour} hours :{minute} minutes :{second} second.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n') # split the responses into lines
    non_empty_lines = [line for line in lines if line.strip()] # remove empty lines
    modified_answer = '\n'.join(non_empty_lines) # joined the cleaned lines back together
    return modified_answer

# Main chatbot function to handle the queries
def ChatBot(Query):

    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:
        # Handle time-related questions directly
        query_lower = Query.lower()
        if "what time" in query_lower or "current time" in query_lower or "time right now" in query_lower or "What's the time right now" in query_lower or "tell me the time" in query_lower or "time" in query_lower or "tell me the current time" in query_lower or "time batao" in query_lower or "abhi time kya hua hay ?" in query_lower or "time bata sakte ho ?" in query_lower or "kitna baza hay abhi ?" in query_lower or "time batana zara" in query_lower or "samay kitana hua ?" in query_lower or "date aur time batao" in query_lower or "tell me the date and time" in query_lower or "sirf time batao" in query_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role":"user", "content": f"{Query}"})

        # make a reques to the Groq API for the response
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize an empty string to store the AI's response.

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>","") # clean up any unwanted tokens from the responses

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f,indent=4)
        return "Sorry, I couldn't connect to the AI service." # retry the query after reseting the chat log

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question :")
        print(ChatBot(user_input))