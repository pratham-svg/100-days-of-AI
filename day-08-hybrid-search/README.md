# Day 8: Hybrid Search — BM25 + Semantic Search

Let's break this down simply, piece by piece based on what I've learned today.

---

## First, why do I even need "hybrid" search?

I already know semantic search (I built RAG with Qdrant on Day 6). It uses embeddings — converts text to vectors and finds meaning-based similarity.

But it has a weakness. If I try searching for **"GPT-4o"** or **"LangGraph v0.2.1"** or someone's name like **"Andrej Karpathy"** in a semantic search system...

Semantic search might return garbage — because embeddings understand _meaning_, not exact keywords. It doesn't know that "GPT-4o" is a specific thing it should match precisely.

That's where BM25 comes in.

---

## What is BM25?

BM25 stands for **Best Match 25**. I won't worry about the name — it's just a fancy version of old-school keyword search.

I like to think of it like a librarian who:

- Counts how many times my search word appears in a document
- Penalizes documents that are very long (just because a word appears 10 times in a 10,000 word doc doesn't make it the best match)
- Rewards documents where my keyword is _rare_ across the whole library (if everyone uses the word "the", it's not useful — but if only 2 docs use "RAGAS evaluation", those docs are probably very relevant)

That last idea — rare words = more valuable — is called **IDF (Inverse Document Frequency)**. BM25 is built on this.

**In simple terms:** BM25 is really good at finding exact keyword matches, rare terms, product names, proper nouns, and version numbers.

---

## What is Semantic Search (recap)?

I know this already. It converts text → vectors → finds documents that are _conceptually similar_ even if the words don't match.

If I search "how do I fix my car" it also returns results about "automobile repair" — different words, same meaning.

**In simple terms:** Semantic search is great at understanding intent and meaning, even with paraphrasing.

---

## So what does each one _fail_ at?

|             | BM25                                          | Semantic Search               |
| ----------- | --------------------------------------------- | ----------------------------- |
| ✅ Great at | Exact keywords, names, codes, version numbers | Meaning, paraphrasing, intent |
| ❌ Bad at   | Understanding meaning                         | Exact keyword matching        |

**Example:** If I search for _"LangGraph checkpointer bug"_

- BM25 finds docs with those exact words ✅
- Semantic search finds docs about "state persistence issues in graph agents" ✅
- Neither alone gives me the full picture

**Hybrid search gives me both.**

---

## How does Hybrid Search actually work?

I'll run **both** searches in parallel and then **combine the scores**.

```
Query → BM25 Search     → Score A
Query → Semantic Search → Score B
         ↓
   Combine A + B (weighted)
         ↓
   Final ranked results
```

The combining step is called **Reciprocal Rank Fusion (RRF)** — the most common method. Instead of trying to normalize two completely different score scales (BM25 scores vs cosine similarity scores), RRF works on _ranks_ instead.

**RRF in plain English:**

- BM25 says doc X is rank #1, doc Y is rank #3
- Semantic says doc Y is rank #1, doc X is rank #5
- RRF combines those ranks with a formula and produces a new unified ranking
- Doc Y probably wins because it ranked high in _both_

---

## Why is this a big deal for my RAG specifically?

My RAG system (from earlier days) retrieved chunks using only semantic search. That works well _most_ of the time. But imagine someone asks:

> _"What does the document say about Section 4.2.1?"_

Semantic search will struggle — "Section 4.2.1" has no _meaning_, it's just a label. BM25 nails it instantly.

Or:

> _"Find everything about the CVE-2024-1234 vulnerability"_

That's a specific code. Semantic search might return generic security docs. BM25 finds the exact match.

**Hybrid = better recall, better precision, fewer hallucinations.**

---

## The implementation picture (what I'll build today)

```
My Query
    ↓
┌─────────────────────────────────┐
│  BM25 Retriever (keyword)       │  → Top K results
│  (rank_bm25 library)            │
└─────────────────────────────────┘
        +
┌─────────────────────────────────┐
│  Qdrant Semantic Retriever      │  → Top K results
│  (I already know this)          │
└─────────────────────────────────┘
        ↓
   RRF Fusion / Weighted merge
        ↓
   Final Top K chunks → LLM
```

---

## Summary in one line each:

- **BM25** = Smart keyword search. Great for exact terms, proper nouns, codes.
- **Semantic Search** = Meaning-based search. Great for intent and paraphrasing.
- **Hybrid Search** = Run both, merge results. Best of both worlds.
- **RRF** = The smart way to combine two ranked lists without caring about different score scales.
