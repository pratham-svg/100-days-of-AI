from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

model= ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
    
)

summary_chain = (
    PromptTemplate.from_template("Summarize this:\n{text}")
    | model
    | StrOutputParser()
)

keyword_chain = (
    PromptTemplate.from_template("Extract 5 keywords:\n{text}")
    | model
    | StrOutputParser()
)

sentiment_chain = (
    PromptTemplate.from_template("What is the sentiment?\n{text}")
    | model
    | StrOutputParser()
)

parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "keywords": keyword_chain,
    "sentiment": sentiment_chain,
})

result = parallel_chain.invoke({
    "text": "AI is transforming industries rapidly..."
})

print(result)