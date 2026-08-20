# This is the Brain Of MY AI 

import cohere
from rich import print
from dotenv import dotenv_values

# Load enviorenmenet variable form the .env file
env_vars = dotenv_values(".env")

# Retrive the API key
CohereAPIKey = env_vars("CohereAPIKey")

# create a cohere api key using the provided api key
co = cohere.Client(api_key=CohereAPIKey)


#  Defined a list of recognized function keywords for task recognization
funcs = [
    "exit" , "general" , "realtime" , "open" , "close" , "play" , " pause"
    "generate image" , "system" , "content" , "google search" , 
    "youtube search" , "remainder"
]

# Initialized a empty list to store the users message
message = []

# define the preamble that guides the ai model on how to catagorixes the queries
preamble = """"""

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
    {"role": "Chatbot", "message": "general chat with me."}
]