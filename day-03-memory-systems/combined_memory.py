from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_classic.chains import ConversationChain
from dotenv import load_dotenv
import os
import tiktoken

load_dotenv()

# --- Custom LLM Wrapper for Arcee Trinity ---
class ArceeChatOpenAI(ChatOpenAI):
    def get_num_tokens_from_messages(self, messages) -> int:
        """Override the token counter to work with custom models."""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except:
            encoding = tiktoken.get_encoding("gpt2")
        
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            num_tokens += len(encoding.encode(message.content))
        return num_tokens

def demo_hybrid_memory():
    print("\n--- 4. Hybrid Memory (Summary + Buffer) Demo ---")
    # Use our custom class instead of raw ChatOpenAI
    llm = ArceeChatOpenAI(
        model="arcee-ai/trinity-large-preview:free",  
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )

    # This memory keeps the most recent messages as RAW text 
    # but summarizes the older ones to save space!
    memory = ConversationSummaryBufferMemory(
        llm=llm, 
        max_token_limit=150, # Try setting this to 50 to see it summarize sooner!
        memory_key="history"
    )

    conversation = ConversationChain(
        llm=llm, 
        memory=memory, 
        verbose=True
    )

    print(conversation.predict(input="Hi! I am Pratham and I'm learning LangChain memory systems."))
    print(conversation.predict(input="I want to build a hybrid system that uses both summary and buffer."))
    print(conversation.predict(input="Tell me about myself and what I am building?"))

    # Let's inspect the memory internally
    print("\n--- Internal Memory Content ---")
    print(memory.load_memory_variables({}))

if __name__ == "__main__":
    demo_hybrid_memory()
