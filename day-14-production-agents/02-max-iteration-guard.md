# 🔁 Max Iteration Guard

If you let them, **Agents can loop forever if the LLM gets confused.**

Sometimes an LLM gets stuck in a rut. It might call a tool with the same bad arguments over and over again. Or the tool's output might thoroughly confuse the reasoning engine, causing it to bounce back and forth between two states without ever producing an answer for the user.

To prevent infinite loops and runaway API costs:
1. You add an "iteration counter" to the `AgentState`.
2. Every time the agent goes through a Thought -> Action loop, you increment this counter.
3. You hard stop at 10 iterations (or whatever number makes sense for your use case).

By enforcing a simple numerical guardrail, you protect your system from burning through tokens indefinitely when the language model inevitably goes off the rails.
