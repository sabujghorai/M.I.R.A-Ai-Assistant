from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os

# Find the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

# Check API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API key not found!")
    exit()

print("✅ API key loaded successfully!")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Send request
response = client.responses.create(
    model="gpt-5.6",
    input="Hello! Introduce yourself in one sentence."
)
print("AI:", response.output_text)