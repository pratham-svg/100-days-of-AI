import json
from typing import Literal

from langchain_core.messages import ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
from agent.state import AgentState
from tools.pr_tools import tools, tools_by_name

# ─────────────────────────────────────────────
# 4. LLM + TOOL BINDING
# ─────────────────────────────────────────────

llm = ChatOpenAI(
    model="anthropic/claude-3.5-haiku",
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
)

llm_with_tools = llm.bind_tools(tools)

# ─────────────────────────────────────────────
# 5. SYSTEM PROMPT 
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior software engineer conducting a Pull Request review.

## YOUR INVESTIGATION PROCESS
When given a PR URL, you MUST follow these steps in order:
1. **PLAN** — First, state your review plan in 2-3 sentences before calling any tools
2. **METADATA** — Call fetch_pr_metadata to understand the PR scope
3. **DIFF** — Call fetch_pr_diff to see the actual code changes  
4. **RISK** — Call assess_risk with the metadata and diff to score the PR
5. **SYNTHESIZE** — Write a structured final report (format below)

## FINAL REPORT FORMAT
Always end with a report in this exact structure:

---
## PR Review: [PR Title] (#[number])

**Author:** [author] | **Branch:** [head] → [base]  
**Size:** [additions] additions, [deletions] deletions across [N] files

### 📋 Summary
[2-3 sentence plain-English explanation of what this PR does and WHY]

### 🔍 Key Changes
[Bullet list of the 3-5 most important changes you observed in the diff]

### ⚠️ Risk Assessment: [LEVEL]
**Score:** [score]/15  
**Recommendation:** [merge recommendation]

**Risk Factors:**
[List the risk factors]

**Positive Signals:**
[List the positive signals]

### 💡 Reviewer Checklist
[3-5 specific things a reviewer should check based on what you saw in the diff]

### 🏷️ Labels Suggested
[1-3 labels that would be appropriate: bug, feature, refactor, docs, breaking-change, etc.]
---

## ERROR HANDLING
If any tool returns an ERROR, explain what went wrong and what information you could still provide.
Never fabricate PR data — only report what the tools returned.
"""

# ─────────────────────────────────────────────
# 6. GRAPH NODES
# ─────────────────────────────────────────────

MAX_ITERATIONS = 10  # safety guard — PR review should never need more than this

def agent_node(state: AgentState) -> AgentState:
    """LLM reasoning node."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "iteration_count": state.get("iteration_count", 0) + 1,
        "error_count": state.get("error_count", 0),
        "pr_context": state.get("pr_context", {}),
    }

def tool_node(state: AgentState) -> AgentState:
    """Tool execution node with full error handling."""
    last_message = state["messages"][-1]
    tool_messages = []
    new_error_count = state.get("error_count", 0)
    pr_context = state.get("pr_context", {})

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        try:
            if tool_name not in tools_by_name:
                result = f"ERROR: Tool '{tool_name}' does not exist. Available: {list(tools_by_name.keys())}"
                new_error_count += 1
            else:
                result = tools_by_name[tool_name].invoke(tool_args)
                result_str = str(result)

                # Cache key tool outputs in pr_context for the final response
                if tool_name == "fetch_pr_metadata" and not result_str.startswith("ERROR"):
                    try:
                        pr_context["metadata"] = json.loads(result_str)
                    except Exception:
                        pass

                if tool_name == "assess_risk" and not result_str.startswith("ERROR"):
                    try:
                        pr_context["risk"] = json.loads(result_str)
                    except Exception:
                        pass

                if result_str.startswith("ERROR"):
                    new_error_count += 1

        except Exception as e:
            result = (
                f"ERROR: Tool '{tool_name}' crashed — "
                f"{type(e).__name__}: {str(e)}"
            )
            print(f"[TOOL CRASH] {tool_name} | {e}")
            new_error_count += 1

        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id,
            name=tool_name,
        ))

    return {
        "messages": tool_messages,
        "iteration_count": state.get("iteration_count", 0),
        "error_count": new_error_count,
        "pr_context": pr_context,
    }

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Routing: continue to tools, or end?
    Also enforces the MAX_ITERATIONS guard.
    """
    # ── Max iteration guard — prevents infinite loops ──
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        print(f"[GUARD] Max iterations ({MAX_ITERATIONS}) reached. Forcing end.")
        return "end"

    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"

# ─────────────────────────────────────────────
# 7. BUILD GRAPH
# ─────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()

agent_graph = build_graph()
