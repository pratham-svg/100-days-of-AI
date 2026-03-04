# Day 9: Re-ranking — Cross-Encoders, ColBERT, and RAGAS Theory

Today is all about taking retrieval to the next level. I already know how to get relevant chunks, but sometimes the top retrieved results aren't exactly the _best_ ones. That's where re-ranking comes in! Let's break down the theory I covered today.

---

## The Core Problem: Fast vs. Accurate

When searching through thousands or millions of documents, I need a retriever that is lightning fast. But fast usually means making compromises on accuracy.
What if I could do a fast, broad search first, and then do a slow, careful reading of just the top results? That's the essence of the **Re-ranking pipeline**.

---

## Bi-Encoders

- **What they do:** They encode the user's query and the document chunks _separately_ into vectors, and then I just compare the vectors (e.g., via Cosine Similarity).
- **Pros:** It is extremely fast. Since documents are pre-computed and stored in a vector database like Qdrant, I only encode the query at runtime.
- **Cons:** It limits how well the model understands the deep relationship between the query and the text.
- **In simple terms:** I used this in my Qdrant setup earlier. It's the standard semantic search.

---

## Cross-Encoders

- **What they do:** Instead of separate embeddings, a Cross-Encoder reads the query and the chunk _together_ at the exact same time through the transformer model. It outputs a relevance score between 0 and 1.
- **Pros:** Extremely accurate because self-attention can look at the query and the chunk simultaneously, understanding deep context.
- **Cons:** Very computationally expensive and incredibly slow. I can't run this on 10,000 documents at runtime.
- **In simple terms:** The gold standard for scoring how well a chunk answers a query, but too slow for wide-scale search.

---

## The Re-ranking Pipeline (The Magic Combo)

Since Bi-Encoders are fast and Cross-Encoders are accurate, I combine them!

1. **Stage 1 (Retrieval):** The Bi-Encoder quickly searches 10,000 documents and finds the top 20 candidates.
2. **Stage 2 (Re-ranking):** The Cross-Encoder carefully reads those top 20 and scores them, giving me the final top 5.

```text
Bi-Encoder (10k → 20)  ➔  Cross-Encoder (20 → 5)
```

Best of both worlds: speed and precision.

---

## ColBERT (Contextualized Late Interaction)

I also learned about ColBERT, which introduces a brilliantly different approach:

- Standard embeddings create **one vector per chunk**.
- ColBERT creates **one vector per _token_**!
- It uses **MaxSim scoring** to compute the maximum similarity between individual query tokens and document tokens.
- **Why it matters:** It acts as a middle ground. It's much faster than a Cross-Encoder but retains a lot of the deep, token-level semantic matching that standard Bi-Encoders miss.

---

## RAGAS Evaluation Metrics

Building RAG is cool, but how do I objectively know it's actually working well? Enter **RAGAS** (RAG Assessment). I learned the 4 core metrics for evaluating my RAG pipeline:

1. **Faithfulness:** Is the generated answer factually derived from the provided context? (Measures generation hallucinations).
2. **Answer Relevancy:** Does the generated answer actually address the user's original question? (Measures generation usefulness).
3. **Context Precision:** Did my retriever put the most relevant chunks at the very top of the results? (Measures ranking quality).
4. **Context Recall:** Did my retriever actually find all the necessary information required to answer the question, or did it miss something? (Measures retrieval completeness).

By tracking these, I can scientifically verify that my RAG system is improving!
