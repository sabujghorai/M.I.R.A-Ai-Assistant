import pygame  # Import pygame library for handeling audio playback
import random  # Import random for generating random choices
import asyncio  # Import asyncio for asynchronous operations
import edge_tts  # Import edge_tts for text-to-speech funtionality
import os
from dotenv import dotenv_values

# Load enviornment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # get the assistantVoice from the enviornment variable

if not AssistantVoice:
    raise ValueError("AssistantVoice missing from .env file (check exact key name/casing).")

DATA_DIR = os.path.join(os.getcwd(), "Data")
os.makedirs(DATA_DIR, exist_ok=True)
SPEECH_PATH = os.path.join(DATA_DIR, "speech.mp3")

# Asynchronous function to convert text to and audio file
async def TextToAudioFile(text) -> None:
    if os.path.exists(SPEECH_PATH):  # check if the file already exists
        os.remove(SPEECH_PATH)  # If it exists, remove it to avoid overwritting error

    # Create the communicate object to generate speech
    # NOTE: it's edge_tts.Communicate (capital C, the class) — edge_tts.communicate
    # (lowercase) is the module itself and is not callable.
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='-15Hz', rate='+8%')
    await communicate.save(SPEECH_PATH)  # save the generated speech as an MP3 file

def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))

            # Initialize pygame mixer for audio playback
            pygame.mixer.init()

            # Load the generated speech file into pygame mixr
            pygame.mixer.music.load(SPEECH_PATH)
            pygame.mixer.music.play()  # play the audio

            # Loop until the audio is done playiung or the funtion stop
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)  # Limit the loop to 10 ticks per second

            return True  # Return truw if the audio played sucessfully

        except Exception as e:  # handle any exceptions during the process
            print(f"Error in TTS: {e}")
            return False  # don't loop forever on a real error

        finally:
            try:
                # call the provided function with false to signal the end of TTS
                func(False)
                if pygame.mixer.get_init():  # only touch the mixer if it actually initialized
                    pygame.mixer.music.stop()  # stop the audio playback
                    pygame.mixer.quit()  # quit the pygame mixur

            except Exception as e:  # Handle any exception during cleanup
                print(f"Error in finally block: {e}")

# Function to manage text-to-speech ith additional response for long text
def TextToSpeach(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # split the text by periods into a list of sentenses

    # List of predefined responses for cases where the text ids too long
    responses = [
        "Baaki ka result chat screen par print kar diya gaya hai, kindly check kar lijiye sir.",
        "Baaki ka text ab chat screen par hai sir, please check kar lijiye.",
        "Baaki ka text aap chat screen par dekh sakte hain sir.",
        "Text ka baaki part ab chat screen par hai sir.",
        "Sir, aapko chat screen par aur bhi text dekhne ko milega.",
        "Baaki ka answer ab chat screen par hai sir.",
        "Sir, please chat screen par dekhiye, baaki ka answer wahin hai.",
        "Complete answer aapko chat screen par mil jayega sir.",
        "Text ka next part chat screen par hai sir.",
        "Sir, more information ke liye chat screen check kar lijiye.",
        "Sir, chat screen par aapke liye aur bhi text hai.",
        "Sir, additional text ke liye chat screen par ek baar dekh lijiye.",
        "Sir, chat screen par padhne ke liye aur bhi text milega.",
        "Sir, baaki ke text ke liye chat screen check kar lijiye.",
        "Sir, baaki ka text chat screen par hai.",
        "Sir, chat screen par aur bhi dekhne ke liye hai, please dekh lijiye.",
        "Sir, text ka continuation chat screen par hai.",
        "Complete answer aapko chat screen par mil jayega, kindly check kar lijiye sir.",
        "Sir, baaki ke text ke liye chat screen check kar lijiye.",
        "Sir, complete answer ke liye chat screen par dekh lijiye."
    ]

    # If the text is very long (more than 4 sentenses and 250 characters), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + " . " + random.choice(responses), func)

    # Otherwise just play the whole text
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it ro TextToSpeach funtion
        TextToSpeach(input("Enter the text: "))