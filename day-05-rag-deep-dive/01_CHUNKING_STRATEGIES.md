# Day 5: Chunking Strategies 🧩

Chunking is the process of breaking a large document into smaller, manageable pieces (chunks). If the chunks are too big, we lose precision; if they are too small, we lose context.

## 📊 Overview of Strategies

```mermaid
graph TD
    A[Raw Document] --> B{Choose Chunking Strategy}
    B -->|Fixed-Size| C[Cut at exact N tokens]
    B -->|Recursive| D[Split sequentially: \n\n ➔ \n ➔ Space]
    B -->|Semantic| E[Split when Embedding topic shifts]
    B -->|Document-Aware| F[Split by Markdown/Headers]

    C -.->|Pros: Fast | Cons: Breaks context| G((Resulting Chunks))
    D -.->|Pros: Structural | Cons: Needs tuning| G
    E -.->|Pros: High Precision | Cons: Expensive| G
    F -.->|Pros: Logical | Cons: Needs clean docs| G
```

### 1️⃣ Fixed-Size Chunking

- **How it Works**: Cuts text at a fixed token/character length.
- **Pros**: Simple and fast.
- **Cons**: May break meaning mid-sentence.

### 2️⃣ Recursive Chunking 🌟 _(Production Standard)_

- **How it Works**: Tries to split logically—first by paragraph (`\n\n`), then by sentence (`\n`), then by word.
- **Pros**: Preserves structure and meaning better than fixed-size.

### 3️⃣ Semantic Chunking

- **How it Works**: Uses similarity between sentences to determine when a topic changes, and splits there.
- **Pros**: High precision.
- **Cons**: Higher computational cost because it requires embedding passes just to chunk.

### 4️⃣ Document-Aware Chunking

- **How it Works**: Uses document structure features like headings, sections, or FAQs.
- **Pros**: Best for technical or legal documents.

---

## 🔄 The Overlap Strategy

To prevent context loss right at the "cut" points, we use **Overlap**.

```mermaid
block-beta
  columns 3
  A["Chunk 1: The quick brown fox jumps"]
  B("Overlap: jumps over")
  C["Chunk 2: over the lazy dog"]
```

- **Why?** It ensures no single idea is completely severed.
- **Result**: Improves retrieval accuracy.
