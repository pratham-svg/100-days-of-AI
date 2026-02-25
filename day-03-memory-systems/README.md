# Day 03: Memory Systems in LangChain

Welcome to Day 3! Today we are moving beyond "one-off" prompts and learning how to make our AI "remember" previous interactions.

## 🧠 What is Memory?

By default, LLMs are **Stateless**. This means every time you send a message, it's like the AI is meeting you for the first time. It has no "memory" of what you said 5 seconds ago.

**Stateful** applications manage this by storing the history and feeding it back to the LLM in every new prompt.

---

## 1. ConversationBufferMemory

The simplest type of memory. It stores the raw text of all previous interactions.

- **Pros:** Extremely simple; keeps the exact wording.
- **Cons:** As the conversation gets long, you will run out of "Tokens" (memory limit of the AI) or it will get very expensive.

## 2. ConversationSummaryMemory

Instead of keeping the raw text, this memory type uses another LLM call to create a **summary** of the conversation so far.

- **Pros:** Saves space; allows for very long conversations.
- **Cons:** It loses the specific details/wording of the original messages.

## 3. Token-aware Memory (ConversationTokenBufferMemory)

This memory keeps the most recent messages in the buffer but flushes the oldest ones based on a **Token Limit**, not just the number of messages.

---

## 🏗️ Structure of Memory

Most memory systems in LangChain work with two main concepts:

1.  **input_key**: What the user said.
2.  **output_key**: What the AI said.
3.  **memory_key**: The variable name where the history is stored (usually `history` or `chat_history`).

---

## 🎯 Exercises for Today

1.  **Warm-up:** Create a `ConversationBufferMemory` and add 3 messages manually to see how it formats them.
2.  **The Forgetful Bot:** Create a `ConversationTokenBufferMemory` with a very low token limit (e.g., 50 tokens). See how it "forgets" the beginning of the chat as you add more messages.
3.  **The Summarizer:** Use `ConversationSummaryMemory` and print the "Summary" after every 2 messages.
4.  **Persistent Chat:** (Advanced) Set up a chat loop where the history is stored in a JSON file locally so that when you restart the script, the AI still remembers you!
