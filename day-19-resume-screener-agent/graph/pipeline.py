from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.screener import screener_agent
from agents.scorer import scorer_agent
from agents.feedback import feedback_agent

def create_pipeline():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("screener", screener_agent)
    workflow.add_node("scorer", scorer_agent)
    workflow.add_node("feedback", feedback_agent)

    # Set entry point
    workflow.set_entry_point("screener")

    # Add conditional edges
    workflow.add_conditional_edges(
        "screener",
        lambda state: "scorer" if state.get("is_relevant") else "feedback"
    )

    # Add regular edges
    workflow.add_edge("scorer", "feedback")
    workflow.add_edge("feedback", END)

    return workflow.compile()

# Compile the pipeline
pipeline = create_pipeline()
