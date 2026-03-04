from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL

llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    temperature=0,
)

SYSTEM_PROMPT = """You are my codebase expert assistant. I am giving you relevant code chunks from a repository.
Answer my question based ONLY on the provided code context.
Always mention the file path and function/class name when referencing code.
If the answer is not in the context, say "I couldn't find this in the indexed codebase."
Be precise and technical."""

USER_PROMPT = """Here are the most relevant code chunks from the repository:

{context}

---
Question: {question}

Answer with specific references to file paths and function names:"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT),
])

chain = prompt | llm | StrOutputParser()


def format_context(chunks: list[dict]) -> str:
    """Formats chunks into a readable context block for the LLM."""
    formatted = []
    for i, chunk in enumerate(chunks, 1):
        formatted.append(
            f"--- Chunk {i} ---\n"
            f"File: {chunk['file_path']} (lines {chunk['start_line']}–{chunk['end_line']})\n"
            f"Type: {chunk['chunk_type']} | Name: {chunk['name']}\n\n"
            f"{chunk['content']}\n"
        )
    return "\n".join(formatted)


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """
    Full answer generation pipeline.
    Returns answer text + source references.
    """
    context = format_context(chunks)
    answer = chain.invoke({"context": context, "question": question})
    
    sources = [
        {
            "file": c["file_path"],
            "function": c["name"],
            "lines": f"{c['start_line']}–{c['end_line']}",
            "rerank_score": round(c.get("rerank_score", 0), 4),
        }
        for c in chunks
    ]
    
    return {
        "answer": answer,
        "sources": sources,
    }
