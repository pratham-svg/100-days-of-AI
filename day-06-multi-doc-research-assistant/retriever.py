import os
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from vector_store import get_vector_store
import config

def get_llm():
    """Initialize OpenRouter LLM via LangChain's ChatOpenAI."""
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is missing in the environment.")
        
    return ChatOpenAI(
        model="google/gemini-2.5-flash", # You can change this to any OpenRouter model
        openai_api_key=openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0
    )

def create_research_chain():
    """
    Sets up the Retriever, Custom Prompt, and Document Chain (Steps 5, 6, 7).
    """
    llm = get_llm()
    vectorstore = get_vector_store()
    
    # Step 5: Retriever Base Setup
    # We will pass the dynamic metadata filters at query time, but here we define the base retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Step 7: Cross-Document Question Prompt
    system_prompt = (
        "You are a meticulous research assistant with access to multiple documents.\n"
        "Answer the question using ONLY information from the provided context below.\n"
        "If the information comes from multiple documents, synthesize it and mention each source clearly.\n"
        "If you cannot find the answer in the context, say so clearly — do NOT hallucinate or guess.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    # Create the document chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # Step 6: Create retrieval chain (returns source documents automatically)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return chain

def query_research_assistant(query: str, topic_filter: str = None):
    """
    Executes a query against the research chain, applying metadata filters if provided.
    """
    # Grab the vectorstore to dynamically build the retriever
    vectorstore = get_vector_store()
    
    search_kwargs = {"k": 5}
    if topic_filter:
        # Applying Qdrant metadata filter formatting conceptually
        # Note: In langchain-qdrant, simple dict filters work for equality
        search_kwargs["filter"] = {"topic": topic_filter}
        
    dynamic_retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    # Rebuild chain with dynamic retriever
    llm = get_llm()
    
    # Using the same prompt setup
    system_prompt = (
        "You are a meticulous research assistant with access to multiple documents.\n"
        "Answer the question using ONLY information from the provided context below.\n"
        "If the information comes from multiple documents, synthesize it and mention each source clearly.\n"
        "If you cannot find the answer in the context, say so clearly — do NOT hallucinate or guess.\n\n"
        "Context:\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    qa_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(dynamic_retriever, qa_chain)
    
    print(f"\nSearching for: '{query}'...")
    response = chain.invoke({"input": query})
    
    return response

if __name__ == "__main__":
    print("--- Testing Retriever & Chain ---")
    
    # Test a query
    test_query = "What do different papers say about chunking strategies?"
    result = query_research_assistant(test_query)
    
    print("\n--- Generated Answer ---")
    print(result["answer"])
    
    print("\n--- Source Documents Retrieved ---\n")
    for i, doc in enumerate(result["context"]):
        # Extracting source attribution
        source_file = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        print(f"Source {i+1}: {source_file} (Page {page})")
