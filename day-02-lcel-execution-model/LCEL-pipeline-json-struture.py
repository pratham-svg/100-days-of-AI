from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file


class Blog(BaseModel):
    title: str = Field(description="Blog title")
    summary: str = Field(description="Short introduction")
    key_points: list[str] = Field(description="Three main points")

parser = JsonOutputParser(pydantic_object=Blog)

model= ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
    
)
prompt = PromptTemplate.from_template(
    """
    Generate a blog about {topic}.
    {format_instructions}
    """
)

chain = (
    prompt.partial(format_instructions=parser.get_format_instructions())
    | model
    | parser
)

result = chain.invoke({"topic": "AI Agents"})
print(result)