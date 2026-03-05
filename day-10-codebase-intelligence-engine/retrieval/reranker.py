from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL, TOP_K_FINAL

# Re-using ChatOpenAI for re-ranking as well
reranker_llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    temperature=0,
)

RERANK_SYSTEM_PROMPT = """You are a code relevance ranker. 
Your task is to rank the provided code chunks based on their relevance to the user's question.
Return only a JSON list of the chunk indices in order of relevance (e.g. [2, 0, 1]).
Rank all provided chunks. Only return the JSON list, no explanation."""

def rerank_results(query: str, candidates: list[dict], top_k: int = TOP_K_FINAL) -> list[dict]:
    """
    Re-ranks hybrid search candidates using an LLM instead of a local cross-encoder.
    """
    if not candidates:
        return []
    
    # Prepare chunk descriptions for the LLM
    chunk_summaries = []
    for i, c in enumerate(candidates):
        chunk_summaries.append(f"Index {i}:\nFile: {c['file_path']} | Name: {c['name']}\nContent: {c['content'][:500]}")
    
    context = "\n\n".join(chunk_summaries)
    
    prompt = f"Question: {query}\n\nCode Chunks:\n{context}\n\nRank the indices by relevance. Return JSON list only:"
    
    try:
        response = reranker_llm.invoke([
            ("system", RERANK_SYSTEM_PROMPT),
            ("user", prompt)
        ])
        
        # Extract JSON list from response
        res_text = response.content.strip()
        match = re.search(r'\[.*\]', res_text)
        if match:
            ranked_indices = json.loads(match.group(0))
        else:
            # Fallback if parsing fails
            print(f"Warning: Could not parse LLM rerank output: {res_text}")
            return candidates[:top_k]

        # Reorder candidates based on LLM ranking
        reranked = []
        seen_indices = set()
        for idx in ranked_indices:
            if 0 <= idx < len(candidates) and idx not in seen_indices:
                candidates[idx]["rerank_score"] = 1.0  # Placeholder score
                reranked.append(candidates[idx])
                seen_indices.add(idx)
        
        # Add any missing candidates at the end just in case
        for i, c in enumerate(candidates):
            if i not in seen_indices:
                c["rerank_score"] = 0.0
                reranked.append(c)

        return reranked[:top_k]
        
    except Exception as e:
        print(f"LLM Reranking failed: {e}. Falling back to default order.")
        return candidates[:top_k]
