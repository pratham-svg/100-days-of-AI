from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_classic.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os


# Load environment variables (Make sure you have OPENAI_API_KEY in your .env)
load_dotenv()

def demo_buffer_memory():
    print("\n--- 1. ConversationBufferMemory Demo ---")
    llm = ChatOpenAI(
            model="arcee-ai/trinity-large-preview:free",  
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )
    
    # memory_key is the variable name used in the prompt
    memory = ConversationBufferMemory()
    
    # ConversationChain is the easiest way to use memory in a "Legacy" way
    # It automatically handles the history for you
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True # This shows us the prompt being sent!
    )

    print(conversation.predict(input="Hi, my name is Pratham!"))
    print(conversation.predict(input="What is my name?"))

def demo_summary_memory():
    print("\n--- 2. ConversationSummaryMemory Demo ---")
    llm = ChatOpenAI(
            model="arcee-ai/trinity-large-preview:free",  
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )
    
    # Summary memory needs an LLM to perform the summarizing!
    memory = ConversationSummaryMemory(llm=llm)
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    print(conversation.predict(input="Today I am learning about LangChain memory systems."))
    print(conversation.predict(input="I also want to learn how to persist this memory to Redis."))
    
    # Let's see the summary it created
    print("\n[Current Summary]:", memory.buffer)

def demo_trump_memory():
    print("\n--- 3. Donald Trump Persona Memory Demo ---")
    llm = ChatOpenAI(
            model="arcee-ai/trinity-large-preview:free",  
            temperature=0.9, # Higher temperature for more persona "flair"
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )

    # Custom Prompt Template for Trump Persona
    template = """The following is a conversation with Donald Trump. 
    He is very boastful, uses superlatives like 'tremendous', 'huge', and 'greatest', 
    and speaks in a very distinct style. He remembers everything perfectly.

    Current conversation:
    {history}
    Human: {input}
    AI:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

    memory = ConversationBufferMemory()
    
    conversation = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True
    )

    print(conversation.predict(input="Hi Donald, what do you think about LangChain memory?"))
    print(conversation.predict(input="Can we build a memory system that is huge?"))

if __name__ == "__main__":
    # Uncomment the one you want to try!
    # demo_buffer_memory()
    demo_summary_memory()
    # demo_trump_memory()
