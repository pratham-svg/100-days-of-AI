from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Load environment variables from .env (API Keys, Base URL)
load_dotenv() 

# 2. Initialize the Chat Model (OpenRouter/OpenAI)
model = ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

# 3. Define the Prompt Template
prompt = PromptTemplate.from_template(
    "Explain {topic} in simple terms."
)

# 4. Initialize Output Parser (Converts model output to string)
parser = StrOutputParser()

# 5. Build the LCEL Chain using the pipe operator (|)
# Flow: Prompt -> Model -> Parser
chain = prompt | model | parser

# 6. Invoke the chain with input data
response = chain.invoke({"topic": "LangChain LCEL"})
print(response)