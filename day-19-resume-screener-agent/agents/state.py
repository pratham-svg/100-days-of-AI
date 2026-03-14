from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    jd: str
    resume_text: str
    is_relevant: bool
    scores: Dict[str, int]
    feedback: str
    similar_candidates: List[Dict[str, Any]]
    final_report: Dict[str, Any]
