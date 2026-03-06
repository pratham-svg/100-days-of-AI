# Day 12: LangGraph Theory and Concepts

Today we cover the core theory behind **LangGraph**, how it builds upon LangChain, and the fundamental concepts that make up Agentic workflows.

## ✅ What LangGraph is and why we need it over LangChain

**LangChain** is great for building simple linear workflows (chains) where you go from Step A to Step B to Step C. However, when you want to build **Agents**—AI systems that can think, use tools, make decisions, and loop back to retry if something fails—LangChain chains become too rigid.

**LangGraph** is built specifically for creating cyclical, State-based Agent workflows. It allows for loops, conditionals, and complex decision-making, giving the LLM the ability to "think" and act dynamically rather than just following a straight line.

---

## ✅ LangGraph Terminology

To build with LangGraph, you need to understand its core building blocks:

- **Node**: A step or an action in your graph. It can be an LLM analyzing text, a Python function executing code, or a tool fetching data.
- **Edge**: The lines connecting the nodes. They dictate the flow—"After Node A is done, go to Node B."
- **Conditional Edge**: A dynamic path that depends on a decision. For example, "If the LLM needs a tool, go to the Tool Node; if it has the final answer, go to the End Node."
- **State**: The memory or the "data payload" that gets updated and passed along as you move from node to node (e.g., the conversation history or intermediate results).
- **Graph**: The overall structure showing how all the Nodes and Edges connect together.
- **Compile**: The step where you take your defined Graph layout and turn it into an actual runnable application or executable function.

---

## ✅ What a Tool is

A **Tool** is a specific function or capability given to the LLM so it can interact with the outside world. Since an LLM is naturally just a text predictor frozen in time, a tool lets it do things like search the web, query a database, or run a calculator.

---

## ✅ ReAct Loop — Thought → Action → Observe → Answer

The **ReAct (Reasoning and Acting)** loop is the fundamental way Agents think and solve problems:

1.  **Thought**: The LLM analyzes the user's request and decides what to do ("I need to find the current weather in London").
2.  **Action**: The LLM calls a specific Tool to get the information ("Call the sequence: `get_weather("London")`").
3.  **Observe**: The Tool executes and returns the actual data back to the LLM ("Current weather is 15°C and cloudy").
4.  **Answer**: The LLM synthesizes the observation into a final, human-readable response. (If the observation wasn't enough, it loops back to **Thought**!).

---

## ✅ How the ReAct prompt works and what gets sent to the LLM

To make the ReAct loop work, a specific **system prompt** is sent to the LLM. It usually looks something like this:

> "You have access to the following tools: [Tool 1, Tool 2]. Use the following format:
> Question: the input question
> Thought: you should always think about what to do
> Action: the action to take (must be one of the tools)
> Action Input: the input to the action
> Observation: the result of the action...
> Final Answer: the final answer to the user."

This prompt continuously guides the LLM to output its response in this exact structured format so the LangGraph system can parse it, execute the requested tool, and feed the observation back into the context window for the next turn.

---

## ✅ Pydantic validation: What it is and where it sits in the flow

**Pydantic** is a data validation library used to ensure data is exactly in the format you expect. In an LLM flow, LLMs occasionally output messy or unpredictable text. We use Pydantic to strictly define the input parameters a Tool requires or the structure of the final output the LLM must return.

It sits as a strict "bouncer" right after the LLM generates an output or right before a Tool is executed, ensuring no malformed data crashes the application.

---

## ✅ Pydantic is pure Python, not LLM-based

It is important to remember that **Pydantic has nothing to do with Artificial Intelligence.** It is a core Python library widely used in traditional software engineering (like FastAPI) to validate data types (e.g., ensuring an age is provided as an integer, not a string). We just borrow it in AI engineering because LLMs are notorious for returning unstructured outputs, and pure Python validation helps tame them.
