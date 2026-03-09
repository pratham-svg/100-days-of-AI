from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

# ─────────────────────────────────────────────
# 1. AGENT STATE
# ─────────────────────────────────────────────
# We track messages + iteration count (max iteration guard)
# + a pr_context dict that tools populate for the final report

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    iteration_count: int       # guards against infinite loops
    error_count: int           # tracks tool failures
    pr_context: dict           # shared context populated by tools
