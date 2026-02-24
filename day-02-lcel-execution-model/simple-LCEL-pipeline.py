from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv() # Load variables from .env file


model = ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

prompt = PromptTemplate.from_template(
    "Explain {topic} in simple terms."
)

parser = StrOutputParser()

chain = prompt | model | parser

response = chain.invoke({"topic": "LangChain LCEL"})
print(response)