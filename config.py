import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

genai.configure(api_key=api_key)

# Expose a configured Gemini model instance for the app
gemini_model = genai.GenerativeModel("gemini-2.0-flash")


