# The Math of Search: Similarity Metrics 📐

When we search a Vector Store, we aren't looking for exact words. We are looking for **Similarity**. In a high-dimensional space (1000+ dimensions), "distance" defines "meaning".

## 1️⃣ Cosine Similarity (The Angle)

This is the most popular metric in RAG.

- **Concept:** It measures the **angle** between two vectors.
- **Rule:** If two vectors point in the same direction, they are highly similar (Score ≈ 1).
- **Why?** It ignores how long the text is (magnitude) and focuses purely on the **direction of meaning**.

## 2️⃣ Dot Product (The Multiplier)

- **Concept:** It multiplies the values of two vectors and adds them up.
- **Rule:** It considers both the **Angle** and the **Length** of the vectors.
- **Note:** If your embeddings are normalized (all the same length), Dot Product is mathematically the same as Cosine Similarity!

## 3️⃣ Euclidean Distance (L2)

- **Concept:** The "straight-line" distance between two points.
- **Rule:** The smaller the distance, the more similar the chunks.
- **Visualization:** Imagine a map; Euclidean distance is the "as the crow flies" distance between two cities.

---

## 🎯 Summary Checklist

| Metric          | What it measures  | When to use                                |
| :-------------- | :---------------- | :----------------------------------------- |
| **Cosine**      | Angle only        | Most semantic searches (standard for RAG). |
| **Dot Product** | Angle + Length    | When text length/importance matters.       |
| **Euclidean**   | Physical Distance | When you want absolute closeness in space. |

**Engineering Tip:** Most modern embedding models (like OpenAI's `text-embedding-3-small`) are optimized for **Cosine Similarity**.
