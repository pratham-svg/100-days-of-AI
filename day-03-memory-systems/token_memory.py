from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.chains import ConversationChain
from dotenv import load_dotenv
import os

load_dotenv()

def demo_window_memory():
    print("\n--- 3. ConversationBufferWindowMemory Demo (k-based) ---")
    llm = ChatOpenAI(
            model="arcee-ai/trinity-large-preview:free",  
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )
    
    # This memory will only keep the last K interactions (Human + AI)
    # It removes older messages by count, not by tokens.
    memory = ConversationBufferWindowMemory(
        k=1 # Keep only the last 2 rounds of conversation
    )
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    print(conversation.predict(input="I want to tell you a long story about my cat..."))
    print(conversation.predict(input="He likes to eat fish every morning at 7 AM."))
    print(conversation.predict(input="His name is Fluffy and he is 5 years old."))
    print(conversation.predict(input="Actually, I forgot, what did I tell you about his breakfast?"))

if __name__ == "__main__":
    demo_window_memory()
