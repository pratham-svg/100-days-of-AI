from langchain_openai import ChatOpenAI
from core.config import settings

def get_llm(temperature: float = 0.2):
    """
    Initialize and return the LLM client using OpenRouter configuration.
    """
    return ChatOpenAI(
        model=settings.OPENROUTER_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "https://github.com/pratham-svg/100-days-of-AI", # Optional
            "X-Title": settings.APP_NAME, # Optional
        }
    )
