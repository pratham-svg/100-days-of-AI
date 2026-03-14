from agents.state import AgentState
from agents.llm import get_llm
from langchain_core.messages import HumanMessage
import json

def screener_agent(state: AgentState) -> AgentState:
    """Agent 1: Check if the resume is relevant to the JD."""
    llm = get_llm()
    
    prompt = f"""
    Job Description:
    {state['jd']}
    
    Resume:
    {state['resume_text']}
    
    Is this resume relevant to the job description? 
    Respond in JSON format:
    {{
        "is_relevant": true/false,
        "reason": "short explanation"
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Try to parse JSON from response
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        state['is_relevant'] = data.get("is_relevant", False)
        print(f"Screener: Relevant={state['is_relevant']}, Reason={data.get('reason')}")
    except Exception as e:
        print(f"Error parsing screener response: {e}")
        state['is_relevant'] = False
        
    return state
