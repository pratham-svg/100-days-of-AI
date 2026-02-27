# Day 5: Similarity Metrics & Core Mental Model 🪐

Once our text is safely transformed into numerical vectors, how do we use them? We search them using geometry.

## 1. Why Cosine Similarity? 📐

If we want to find out how similar two text chunks are, we compare their vectors.

- **Euclidean Distance**: Measures physical straight-line distance. It is sensitive to vector length (e.g., how long the sentence is).
- **Cosine Similarity**: Measures the _angle_ (direction) between two vectors.

```mermaid
graph LR
    A[Vector A: 'Hi']
    B[Vector B: 'Greetings']
    C[Vector C: 'A really long greeting message!']

    A -->|Direction aligns| B
    A -->|Direction aligns| C
```

- **The Rule**: In embedding space, **Direction = Meaning**.
- Two vectors pointing in the exact same direction have a Cosine Similarity of `1`. Opposite directions = `-1`.

## 2. The Core Mental Model of RAG ⚙️

RAG is less about matching keywords, and more about finding the nearest conceptual neighbor.

```mermaid
graph TD
    A[Raw Document] -->|Smart Chunking| B[Chunks]
    B -->|Semantic Projection| C[(Vector DB)]

    D[User Question] -->|Embeds into Vector| E(Query Vector)

    E -->|Nearest Neighbor Search| C
    C -->|Retrieves top similar Chunks| F[Context Injection]
    F -->|Passed as prompt to| G[LLM Generation]
    G --> H[Final Answer!]

    style C fill:#f3e5f5,stroke:#7b1fa2
    style G fill:#fff3e0,stroke:#e65100
```

### The 3 Core Pillars:

1. **Language becomes Geometry**: Words translate into high-dimensional points.
2. **Meaning becomes Distance**: Similar ideas are mathematically closer together.
3. **Retrieval becomes Search**: RAG simply queries the closest "Meaning" points to your question.
