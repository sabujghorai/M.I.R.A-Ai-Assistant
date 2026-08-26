import asyncio
from random import randint
from PIL import Image
import io
from dotenv import get_key
import os
from time import sleep
from huggingface_hub import InferenceClient

# Directories/files
DATA_DIR = os.path.join(os.getcwd(), "Data")
FRONTEND_DATA_FILE = os.path.join(os.getcwd(), "Frontend", "Files", "ImageGeneration.data")

# Ensure required folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FRONTEND_DATA_FILE), exist_ok=True)

# Ensure the data file itself exists, with safe default content
if not os.path.exists(FRONTEND_DATA_FILE):
    with open(FRONTEND_DATA_FILE, "w") as f:
        f.write("None,False")
    print(f"[ImageGeneration] Created missing data file at {FRONTEND_DATA_FILE}")


def open_image(prompt):
    """Open and display generated images for a given prompt."""
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(DATA_DIR, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening Image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


# Hugging Face Inference client (replaces the deprecated api-inference.huggingface.co direct calls)
client = InferenceClient(token=get_key(".env", "HuggingFaceAPIKey"))

# How many images to generate per prompt. Lower this if you're low on Inference credits.
IMAGES_PER_PROMPT = 1  # was 4 — reduced to conserve free-tier credits

# Model to use for text-to-image generation
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"


async def query(prompt_text):
    """Send one text-to-image request via the Hugging Face Inference client."""
    image = await asyncio.to_thread(
        client.text_to_image,
        prompt_text,
        model=IMAGE_MODEL,
    )
    # image is a PIL.Image — convert to JPEG bytes for saving
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


async def generate_images(prompt: str):
    """Generate IMAGES_PER_PROMPT images concurrently and save them to disk."""
    tasks = []
    for _ in range(IMAGES_PER_PROMPT):
        full_prompt = (
            f"{prompt}, quality=4K, sharpness=maximum, "
            f"Ultra High details, high resolution, seed={randint(0, 1000000)}"
        )
        task = asyncio.create_task(query(full_prompt))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        file_path = os.path.join(DATA_DIR, f"{prompt.replace(' ', '_')}{i+1}.jpg")
        with open(file_path, "wb") as f:
            f.write(image_bytes)


def GenerateImage(prompt: str):
    """Wrapper function to generate and open image(s) for a prompt."""
    asyncio.run(generate_images(prompt))
    open_image(prompt)


# Main loop to monitor for image generation requests
while True:
    try:
        with open(FRONTEND_DATA_FILE, "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.strip().split(",")
        Status = Status.strip()

        if Status == "True":
            print("Generating Images...")
            try:
                GenerateImage(prompt=Prompt)
            except Exception as gen_error:
                print(f"[ImageGeneration] Generation failed: {gen_error}")
            finally:
                # Always reset the file, whether generation succeeded or failed —
                # prevents an infinite retry storm hammering the API on repeated failures.
                with open(FRONTEND_DATA_FILE, "w") as f:
                    f.write("False,False")
            break  # exit the loop after processing this request
        else:
            sleep(1)  # wait for 1 second before checking again

    except :
        pass