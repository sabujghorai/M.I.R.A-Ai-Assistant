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
    "The rest of the result has been printed on the chat screen, kindly check it, sir.",
    "The rest of the text is now on the chat screen, sir, please check it.",
    "You can see the rest of the text on the chat screen, sir.",
    "The remaining part of the text is now on the chat screen, sir.",
    "Sir, you'll find more text to see on the chat screen.",
    "The rest of the answer is now on the chat screen, sir.",
    "Sir, please look at the chat screen, the rest of the answer is there.",
    "You'll get the complete answer on the chat screen, sir.",
    "The next part of the text is on the chat screen, sir.",
    "Sir, please check the chat screen for more information.",
    "Sir, there's more text for you on the chat screen.",
    "Sir, please take a look at the chat screen for the additional text.",
    "Sir, you'll find more text to read on the chat screen.",
    "Sir, please check the chat screen for the rest of the text.",
    "Sir, the rest of the text is on the chat screen.",
    "Sir, there's more to see on the chat screen, please take a look.",
    "Sir, the continuation of the text is on the chat screen.",
    "You'll get the complete answer on the chat screen, kindly check it, sir.",
    "Sir, please check the chat screen for the rest of the text.",
    "Sir, please look at the chat screen for the complete answer."
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