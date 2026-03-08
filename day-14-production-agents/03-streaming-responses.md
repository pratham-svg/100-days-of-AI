# ⚡ Streaming Responses

Nobody wants to stare at a blank screen waiting for an answer.

Instead of making users wait for the full answer (which could take 10+ seconds for complex agentic workflows), **you stream tokens in real time**. 

You can accomplish this using **Server-Sent Events (SSE)** in FastAPI, for example. 

By streaming the response:
1. Users see the agent "thinking" in real-time.
2. They see which tools are being called and what parameters are being passed.
3. The answer appears live as it's being generated.

This transforms the psychological experience of waiting into an engaging experience of watching a process unfold.
