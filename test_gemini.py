
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not api_key:
    raise SystemExit("GEMINI_API_KEY not found in .env")

try:
    client = genai.Client(api_key=api_key)

    print("Connecting to Gemini...")

    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: COD RTO Gemini connection successful."
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as error:
    print("\nGEMINI CONNECTION FAILED")
    print(error)
