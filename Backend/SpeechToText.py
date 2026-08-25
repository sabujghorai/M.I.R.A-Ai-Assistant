from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load enviornment variables from the .env file
env_vars = dotenv_values(".env")
# Get the input language setting from the enviornment variables
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speach recognization interface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognitionCtor();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language settig in the HTML code with the input language fromt he enviornment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# get the current working directory
currnet_dir = os.getcwd()

# make sure the Data folder actually exists, then write into it with a real cross-platform path
os.makedirs(os.path.join(currnet_dir, "Data"), exist_ok=True)
VoiceHtmlPath = os.path.join(currnet_dir, "Data", "Voice.html")
with open(VoiceHtmlPath, "w") as f:
    f.write(HtmlCode)

# Generate the file path for the HTML file
Link = f"file://{VoiceHtmlPath}"

# set chrome option to the webdriver
chrome_option = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_option.add_argument(f'user-agent={user_agent}')
chrome_option.add_argument("--use-fake-ui-for-media-stream")
chrome_option.add_argument("--use-fake-device-for-media-stream")
chrome_option.add_argument("--headless=new")
# Initialize the chrome webdriver using the chromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_option)

# Define the path for temporary files
TempDirPath = rf"{currnet_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "when","why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    # check if the query is a question and add question mark if necessary.
    if any(word + " " in new_query for word in query_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Functiuon to Translate text into english using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speach recognition using the webdriver
def SpeechRecognition():
    try:
        # Open the html file in the browser
        driver.get(Link)
        # Start speech recognition by clicking the start button
        driver.find_element(by=By.ID, value="start").click()
        print("Listening...")
    except Exception as e:
        print(f"[startup failed] {e}")
        return None

    while True:
        try:
            # Get the recognized text from the html output element
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                driver.find_element(by=By.ID, value="end").click()

                # if the input language is english, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, Translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))

        except Exception as e:
            print(f"[loop error] {e}")
            continue

if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            if Text:
                print(Text)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        driver.quit()