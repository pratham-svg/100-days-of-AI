from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 

# 1. Define the desired JSON structure using Pydantic
class Blog(BaseModel):
    title: str = Field(description="Blog title")
    summary: str = Field(description="Short introduction")
    key_points: list[str] = Field(description="Three main points")

# 2. Initialize the JSON Output Parser with our Pydantic model
parser = JsonOutputParser(pydantic_object=Blog)

# 3. Setup the Chat Model
model= ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

# 4. Define Prompt with format_instructions placeholder
prompt = PromptTemplate.from_template(
    """
    Generate a blog about {topic}.
    {format_instructions}
    """
)

# 5. Build the chain
# We use .partial() to inject the parser's specific formatting rules into the prompt
chain = (
    prompt.partial(format_instructions=parser.get_format_instructions())
    | model
    | parser
)

# 6. Execute the chain and print the structured JSON results
result = chain.invoke({"topic": "AI Agents"})
print(result)