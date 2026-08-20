from groq import Groq # importing the groq library to use the API  
from json import load,dump # importing function to read and write the json file
import datetime # for real time date and time information
from dotenv import dotenv_values # importing the dotenv_values to read enviornment variables from a .env file


env_vard = dotenv_values(".env")

# Retrive specific envirenment variables for username,assistant name and API keys
Username = env_vard.get("username")
Assistantname = env_vard.get("Assistantname")
GroqAPIKey = env_vard.get("GroqAPIKey")

# initializing the Groq client using the provided API key
client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""
Hello, I am {Username}. You are {Assistantname}, a very accurate and advanced AI voice assistant.

Your job is to assist {Username} quickly, accurately, and naturally.

Rules:
- Do not tell the current time unless I specifically ask for it.
- Keep your responses short and direct.
- Answer only what I asked.
- Always reply in English, even if I speak Hindi or another language.
- Do not provide unnecessary notes or explanations.
- Never mention your training data.
- Do not say that you are unable to perform a task unless it is genuinely impossible.
- Be polite, helpful, and natural.
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
    """ This function sends the user's query to the chatbot and returns the AI's response. """

    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role":"user", "content": f"{Query}"})

        # make a reques to the Groq API for the response
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
        return ChatBot(Query) # retry the query after reseting the chat log

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question :")
        print(ChatBot(user_input))