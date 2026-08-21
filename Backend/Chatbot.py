from groq import Groq # importing the groq library to use the API  
from json import load,dump # importing function to read and write the json file
import datetime # for real time date and time information
from dotenv import dotenv_values # importing the dotenv_values to read enviornment variables from a .env file
import requests
import re


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

# This get weather function will tell the realtime weather information to me..
def GetWeather(city):
    """Get real-time weather for any city/place."""

    try:

        # ==========================================
        # STEP 1: FIND LOCATION
        # ==========================================

        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 5,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"I couldn't find a place called {city}."

        # Take the best matching location
        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location.get("name", city)
        country = location.get("country", "")

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "rain,"
                "showers,"
                "snowfall,"
                "weather_code,"
                "cloud_cover,"
                "wind_speed_10m,"
                "wind_direction_10m"
            ),

            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_data = weather_response.json()
        if "current" not in weather_data:
            return "I couldn't get the current weather information."

        current = weather_data["current"]
        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        feels_like = current["apparent_temperature"]
        precipitation = current["precipitation"]
        rain = current["rain"]
        showers = current["showers"]
        snowfall = current["snowfall"]
        weather_code = current["weather_code"]
        cloud_cover = current["cloud_cover"]
        wind_speed = current["wind_speed_10m"]
        wind_direction = current["wind_direction_10m"]

        weather_description = {

            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "foggy",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "heavy drizzle",
            56: "light freezing drizzle",
            57: "heavy freezing drizzle",
            61: "light rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "light freezing rain",
            67: "heavy freezing rain",
            71: "light snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "light rain showers",
            81: "moderate rain showers",
            82: "heavy rain showers",
            85: "light snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with light hail",
            99: "thunderstorm with heavy hail",
            100: "Baarish ki samvawna thoda thoda hay",
            101: "aasmaan saaf hai",
            102: "zyadaatar aasman saaf hai",
            103: "aasman mein kuch baadal hain",
            104: "poora aasman baadalon se dhaka hai",
            105: "kohra hai",
            106: "kohra hai",
            107: "halki boonda baandi ho rahi hai",
            108: "madhyam boonda baandi ho rahi hai",
            109: "tez boonda baandi ho rahi hai",
            110: "halki jamne wali boonda baandi ho rahi hai",
            111: "tez jamne wali boonda baandi ho rahi hai",
            112: "halki baarish ho rahi hai",
            113: "madhyam baarish ho rahi hai",
            114: "tez baarish ho rahi hai",
            115: "halki jamne wali baarish ho rahi hai",
            116: "tez jamne wali baarish ho rahi hai",
            117: "halki barfbaari ho rahi hai",
            118: "madhyam barfbaari ho rahi hai",
            119: "tez barfbaari ho rahi hai",
            120: "barf ke chhote daane gir rahe hain",
            121: "halki baarish ki bauchhaar ho rahi hai",
            122: "madhyam baarish ki bauchhaar ho rahi hai",
            123: "tez baarish ki bauchhaar ho rahi hai",
            124: "halki barf ki bauchhaar ho rahi hai",
            125: "tez barf ki bauchhaar ho rahi hai",
            126: "garaj ke saath toofan aa raha hai",
            127: "halki ole ke saath garaj wala toofan aa raha hai",
            128: "tez ole ke saath garaj wala toofan aa raha hai"
        }

        condition = weather_description.get(
            weather_code,
            "unknown weather"
        )

        if rain > 0 or showers > 0:
            rain_status = "It is currently raining."

        elif precipitation > 0:
            rain_status = "There is some precipitation."

        else:

            rain_status = "There is no significant rain right now."

        result = (
            f"\nCurrently in {city_name}, {country}, \n"
            f"the temperature is {temperature} degrees Celsius ,"
            f"with {condition}. \n"
            f"And It feels like {feels_like} degrees. \n"
            f"Humidity is {humidity} percent. \n"
            f"Cloud cover is {cloud_cover} percent. \n"
            f"Wind speed is {wind_speed} kilometers per hour. \n"
            f"{rain_status}\n"
        )

        return result

    except requests.RequestException:
        return "I couldn't connect to the weather service right now."

    except Exception as e:
        print(f"Weather Error: {e}")

        return "I couldn't get the weather information right now."


# for finding the place and giving me the answer
def ExtractWeatherPlace(query):
    """Extract the location from a weather-related question."""

    query = query.strip()
    patterns = [

        r"(?:weather|temperature|forecast)\s+(?:of|in|at|for)\s+(.+)",
        r"(?:weather|temperature|forecast)\s+(?:of|in|at|for)?\s*(.+)",
        r"(?:is it raining|is it sunny|is it cloudy)\s+(?:in|at)\s+(.+)",
        r"(?:how hot|how cold)\s+(?:is it)\s+(?:in|at)\s+(.+)",
        r"(?:what's|what is|how is|how's)\s+(?:the )?(?:weather|temperature)"
        r"\s+(?:like )?(?:in|at|of|for)\s+(.+)",
        r"(?:will it rain)\s+(?:in|at)\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:
            place = match.group(1).strip()
            # Remove question marks
            place = place.rstrip("?.!")
            return place

    return None



# Main chatbot function to handle the queries
def ChatBot(Query):

    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:

        query_lower = Query.lower()

        if (
            "what time" in query_lower
            or "current time" in query_lower
            or "time right now" in query_lower
            or "what's the time right now" in query_lower
            or "tell me the time" in query_lower
            or "time" in query_lower
            or "tell me the current time" in query_lower
            or "time batao" in query_lower
            or "abhi time kya hua hay ?" in query_lower
            or "time bata sakte ho ?" in query_lower
            or "kitna baza hay abhi ?" in query_lower
            or "time batana zara" in query_lower
            or "samay kitana hua ?" in query_lower
            or "date aur time batao" in query_lower
            or "tell me the date and time" in query_lower
            or "sirf time batao" in query_lower
            or "date aur time batana" in query_lower
        ):

            current_time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            return f"The current time is {current_time}."


        weather_keywords = [
            "weather",
            "weather in",
            "temperature",
            "temperature in",
            "forecast",
            "forecast in",
            "raining",
            "raining in",
            "rain",
            "rain in",
            "sunny",
            "sunny in",
            "cloudy",
            "cloudy in",
            "how hot",
            "how hot in",
            "how cold",
            "how cold in"
        ]

        if any(keyword in query_lower for keyword in weather_keywords):

            # Find the place from the user's question
            city = ExtractWeatherPlace(Query)

            # If a place was successfully detected
            if city:
                weather_result = GetWeather(city)
                return weather_result
            
            else:
                return (
                    "Sure. Which place would you like "
                    "me to check the weather for?"
                )

        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({
            "role": "user",
            "content": f"{Query}"
        })

        completion = client.chat.completions.create(

            model="openai/gpt-oss-20b",
            messages=(
                SystemChatBot
                + [
                    {
                        "role": "system",
                        "content": RealtimeInformation()
                    }
                ]
                + messages
            ),

            max_tokens=1024,
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
        messages.append({
            "role": "assistant",
            "content": Answer
        })

        with open(r"Data\ChatLog.json", "w") as f:
            dump(
                messages,
                f,
                indent=4
            )
        return AnswerModifier(
            Answer=Answer
        )

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:

            dump(
                [],
                f,
                indent=4
            )

        return "Sorry, I couldn't connect to the AI service." # retry the query after reseting the chat log

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question :")
        print("M.I.R.A : ",ChatBot(user_input))