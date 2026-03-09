import os
from dotenv import load_dotenv

# Load from the local .env file
load_dotenv()
# Fallback to check parent directory if needed
load_dotenv("../.env") 

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
