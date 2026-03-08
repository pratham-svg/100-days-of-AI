# 🛡️ Error Handling in Tools

Theory is easy. Making agents that don't break in the real world — that's the actual work.

**When a tool fails it should never crash the agent.** 

If you're querying a database and the connection drops, or scraping an API and you hit a rate limit, the default behavior of an unhandled exception is to blow up the whole system. That's a bad User Experience.

Instead:
1. You catch the error inside the tool definition.
2. You return that error string as the tool's output back to the LLM as a regular message.
3. Because the LLM receives the error text directly, it can reason about it ("Ah, that tool call failed due to a missing parameter, let me try again with the right one").

The agent recovers gracefully, adapts, and tries again instead of crashing.
