from agents.state import AgentState
from agents.llm import get_llm
from langchain_core.messages import HumanMessage
import json

def scorer_agent(state: AgentState) -> AgentState:
    """Agent 2: Score the resume across 5 dimensions."""
    if not state.get('is_relevant'):
        return state
        
    llm = get_llm()
    
    prompt = f"""
    Job Description:
    {state['jd']}
    
    Resume:
    {state['resume_text']}
    
    Score this resume from 0-100 on the following criteria:
    1. skills_match
    2. experience_level
    3. education
    4. project_relevance
    5. overall_fit
    
    Respond ONLY in JSON format:
    {{
        "skills_match": 85,
        "experience_level": 70,
        "education": 60,
        "project_relevance": 80,
        "overall_fit": 75
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        scores = json.loads(content)
        state['scores'] = scores
        print(f"Scorer: {scores}")
    except Exception as e:
        print(f"Error parsing scorer response: {e}")
        state['scores'] = {}
        
    return state
