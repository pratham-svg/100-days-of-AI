from agents.state import AgentState
from agents.llm import get_llm
from langchain_core.messages import HumanMessage

def feedback_agent(state: AgentState) -> AgentState:
    """Agent 3: Provide human-readable feedback and compile final report."""
    if not state.get('is_relevant'):
        state['feedback'] = "Resume not relevant to the job description."
        state['final_report'] = {
            "is_relevant": False,
            "feedback": state['feedback']
        }
        return state
        
    llm = get_llm()
    
    prompt = f"""
    Job Description:
    {state['jd']}
    
    Resume:
    {state['resume_text']}
    
    Scores:
    {state['scores']}
    
    Provide constructive feedback for this candidate based on their match for the job.
    Keep it professional and concise (2-3 sentences).
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    state['feedback'] = response.content.strip()
    
    # Compile final report
    state['final_report'] = {
        "is_relevant": state['is_relevant'],
        "scores": state['scores'],
        "feedback": state['feedback']
    }
    
    print(f"Feedback: {state['feedback']}")
    return state
