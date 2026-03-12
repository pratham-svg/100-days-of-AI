# Day 16: Revision — Deep Diving into State & Routing 🔄

Before jumping into multi-agent systems, it was time to stop and audit. Code that "just works" isn't enough; I needed to understand *why* it works to ensure scalability.

## 🧠 AgentState: The Living Memory

The `AgentState` isn't just a data container; it's the agent's entire living memory. 

*   **The Chain of Events:** Every turn gets appended—Human Message ➡️ LLM Response ➡️ Tool Call ➡️ Tool Result.
*   **The Full Picture:** The LLM reads this entire growing list on **every single iteration**. This context is what allows it to decide its next move with precision.

## 🚦 Guardrails: Protecting the Loop

The `iterations` count exists for one critical reason: **Safety.** Without a max iteration guard, an agent can get stuck in an infinite loop of calling the same tools, draining your API credits and hanging the system.

---

## 🔀 The ReAct Routing Mechanism

The routing logic finally clicked today. It's simpler than it looks:

1.  **The LLM (The Brain):** Decides whether to act by including `tool_calls` in its output or just plain text.
2.  **should_continue (The Postman):** Simply reads the LLM's output. 
    *   If `tool_calls` exist? Send it to the Tool Node.
    *   No `tool_calls`? Send it to the END.

> **Mental Model:** The LLM is the brain making the choice. The router is just the postman delivering the execution to the right node.

---

## ⚖️ The Growing Messages Problem

As the conversation goes on, the list of messages grows. This leads to four major issues:
1.  **Higher Cost:** Every turn sends more tokens back to the LLM.
2.  **Slower Responses:** LLMs take longer to process massive contexts.
3.  **Context Window Limits:** Eventually, you run out of space.
4.  **Hallucinations:** Overwhelming an LLM with too much history can cause it to lose track of the core task.

**The Solution:** You must implement **trimming** or **summarization** strategies before the history gets out of hand.

---

## 🎯 Reflection
Revision isn't wasted time. It's the difference between code that works once and code that can be extended into a complex multi-agent system.

#100DaysOfAI #LangGraph #AIEngineering #LLM #LangChain #Agents #ReAct #BuildInPublic #MachineLearning
