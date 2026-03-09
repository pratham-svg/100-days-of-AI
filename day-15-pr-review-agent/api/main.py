from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.state import AgentState
from agent.graph import agent_graph, MAX_ITERATIONS
from tools.pr_tools import tools_by_name
from config import GITHUB_TOKEN, OPENROUTER_API_KEY

# ─────────────────────────────────────────────
# 8. FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="GitHub PR Summarizer Agent",
    description="Production LangGraph agent that reviews PRs like a senior engineer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ──

class PRReviewRequest(BaseModel):
    pr_url: str

    @field_validator("pr_url")
    @classmethod
    def validate_pr_url(cls, v):
        if not v or not v.strip():
            raise ValueError("pr_url cannot be empty")
        if "github.com" not in v:
            raise ValueError("pr_url must be a GitHub URL")
        if "/pull/" not in v:
            raise ValueError("pr_url must contain /pull/ — e.g. https://github.com/owner/repo/pull/123")
        return v.strip()


class PRReviewResponse(BaseModel):
    pr_url: str
    report: str                 # full markdown report from the LLM
    risk_level: str | None      # extracted from assess_risk tool
    risk_score: int | None
    tools_called: list[str]
    iterations: int
    error_count: int
    reviewed_at: str


@app.post("/review", response_model=PRReviewResponse)
async def review_pr(request: PRReviewRequest):
    """
    Review a GitHub Pull Request.
    
    The agent will:
    1. Plan its investigation
    2. Fetch PR metadata and diff from GitHub
    3. Assess risk based on patterns
    4. Return a structured senior-engineer-quality review
    
    Example body: { "pr_url": "https://github.com/facebook/react/pull/27456" }
    """
    try:
        initial_state: AgentState = {
            "messages": [
                HumanMessage(
                    content=f"Please review this Pull Request: {request.pr_url}\n\n"
                            f"Follow your investigation process: plan first, then fetch metadata, "
                            f"then the diff, then assess risk, then write the full structured report."
                )
            ],
            "iteration_count": 0,
            "error_count": 0,
            "pr_context": {},
        }

        final_state = await agent_graph.ainvoke(initial_state)

        # ── Extract final AI report ──
        report = ""
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                report = msg.content
                break

        # ── Extract tools called ──
        tools_called = [
            msg.name
            for msg in final_state["messages"]
            if isinstance(msg, ToolMessage)
        ]

        # ── Extract risk from cached pr_context ──
        risk = final_state.get("pr_context", {}).get("risk", {})
        risk_level = risk.get("risk_level")
        risk_score = risk.get("risk_score")

        return PRReviewResponse(
            pr_url=request.pr_url,
            report=report or "Agent completed but produced no report.",
            risk_level=risk_level,
            risk_score=risk_score,
            tools_called=tools_called,
            iterations=final_state.get("iteration_count", 0),
            error_count=final_state.get("error_count", 0),
            reviewed_at=datetime.now().isoformat(),
        )

    except Exception as e:
        print(f"[AGENT ERROR] {datetime.now().isoformat()} | {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent failed: {type(e).__name__}: {str(e)}"
        )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "tools": list(tools_by_name.keys()),
        "max_iterations": MAX_ITERATIONS,
        "github_token_set": bool(GITHUB_TOKEN),
        "openrouter_key_set": bool(OPENROUTER_API_KEY),
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
# 9. QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    async def test():
        # Use any real public GitHub PR URL
        test_url = "https://github.com/tiangolo/fastapi/pull/11657"

        print("=" * 70)
        print(f"Testing PR Review Agent")
        print(f"PR: {test_url}")
        print("=" * 70)

        state: AgentState = {
            "messages": [
                HumanMessage(
                    content=f"Please review this Pull Request: {test_url}\n\n"
                            "Follow your investigation process completely."
                )
            ],
            "iteration_count": 0,
            "error_count": 0,
            "pr_context": {},
        }

        result = await agent_graph.ainvoke(state)

        print(f"\nIterations: {result['iteration_count']}")
        print(f"Errors: {result['error_count']}")
        print(f"\nTools called:")
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                print(f"  ✓ {msg.name}")

        print(f"\n{'=' * 70}")
        print("FINAL REPORT:")
        print("=" * 70)
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                print(msg.content)
                break

    asyncio.run(test())
