import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_qdrant_url():
    url = os.getenv("QDRANT_URL")
    if not url:
        raise ValueError("QDRANT_URL is missing in the .env file")
    return url

def get_qdrant_api_key():
    key = os.getenv("QDRANT_API_KEY")
    if not key:
        raise ValueError("QDRANT_API_KEY is missing in the .env file")
    return key

def get_openai_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is missing in the .env file")
    return key

if __name__ == "__main__":
    print("Testing config script...")
    print("Checking if required keys are present (will error if not set):")
    try:
        qdrant_url = get_qdrant_url()
        print(f"Loaded Qdrant URL: {qdrant_url}")
        
        qdrant_key = get_qdrant_api_key()
        print("Loaded Qdrant API Key: [HIDDEN]")
        
        openai_key = get_openai_api_key()
        print("Loaded OpenAI API Key: [HIDDEN]")
        
        print("\nAll configuration variables loaded successfully.")
    except Exception as e:
        print(f"\nConfiguration Error: {e}")
        print("Please make sure you have created a `.env` file based on `.env.example`.")
