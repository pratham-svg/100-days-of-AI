from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

app = FastAPI(title="LangChain Memory API")

# We use a dictionary to store memory objects for different users (sessions)
# In a real app, you would use Redis or a Database here!
sessions_memory = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. Get or Create memory for this specific session
    if request.session_id not in sessions_memory:
        sessions_memory[request.session_id] = ConversationBufferMemory()
    
    memory = sessions_memory[request.session_id]
    
    # 2. Setup the LLM and Chain
    llm = ChatOpenAI(
            model="arcee-ai/trinity-large-preview:free",  
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )
    conversation = ConversationChain(llm=llm, memory=memory)
    
    # 3. Get the response
    try:
        response = conversation.predict(input=request.message)
        return {
            "session_id": request.session_id,
            "response": response,
            "history_count": len(memory.chat_memory.messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions_memory:
        return {"messages": []}
    
    memory = sessions_memory[session_id]
    return {"messages": [m.content for m in memory.chat_memory.messages]}

if __name__ == "__main__":
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
