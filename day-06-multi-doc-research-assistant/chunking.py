from langchain.text_splitter import RecursiveCharacterTextSplitter
from document_loader import load_documents_with_metadata

def chunk_documents(docs):
    print("\nApplying chunking strategies...")
    
    # Strategy 1: Smaller chunks, less overlap
    splitter_small = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    # Strategy 2: Larger chunks, larger overlap (better for context spanning paragraphs)
    splitter_large = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks_small = splitter_small.split_documents(docs)
    chunks_large = splitter_large.split_documents(docs)
    
    print(f"\nTotal original pages: {len(docs)}")
    print(f"Strategy 1 (size 500, overlap 50) produced: {len(chunks_small)} chunks")
    print(f"Strategy 2 (size 1000, overlap 200) produced: {len(chunks_large)} chunks\n")
    
    if len(chunks_large) > 1:
        print("--- Inspecting Overlap in Strategy 2 (1000/200) ---")
        print("End of Chunk 1:\n", repr(chunks_large[0].page_content[-150:]))
        print("\nStart of Chunk 2:\n", repr(chunks_large[1].page_content[:150]))
        
        # Verify metadata is preserved
        print("\nMetadata of Chunk 1:", chunks_large[0].metadata)
        
    return chunks_large

if __name__ == "__main__":
    print("--- Step 3: Chunking Strategy ---")
    documents = load_documents_with_metadata()
    if documents:
        chunks = chunk_documents(documents)
