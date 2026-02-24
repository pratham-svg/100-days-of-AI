from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 

# 1. Initialize the shared model
model= ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",  
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

# 2. Define multiple independent chains
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

# 3. Combine chains into a parallel execution map
# All these tasks will run simultaneously!
parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "keywords": keyword_chain,
    "sentiment": sentiment_chain,
})

# 4. Invoke the parallel chain with the single common input
result = parallel_chain.invoke({
    "text": "AI is transforming industries rapidly..."
})

# 5. Output will be a dictionary with keys: 'summary', 'keywords', 'sentiment'
print(result)