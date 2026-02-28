import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

# Assuming the PDFs are in a 'pdf' folder inside the day-06 folder
PDF_DIR = Path(__file__).parent / "pdf"

def load_documents_with_metadata():
    docs = []
    if not PDF_DIR.exists():
        print(f"Directory {PDF_DIR} does not exist. Please create it and add PDFs.")
        return docs

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}.")
        return docs

    for file_path in pdf_files:
        print(f"Loading {file_path.name}...")
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        # Add custom metadata (Step 2 focus)
        for page in pages:
            # You can customize these tags based on your specific PDFs
            page.metadata["source_file"] = file_path.name
            page.metadata["topic"] = "LLM Engineering & RAG"
            
        docs.extend(pages)
        
    print(f"\nSuccessfully loaded a total of {len(docs)} pages.")
    return docs

if __name__ == "__main__":
    print("--- Step 2: Document Loading with Metadata ---")
    documents = load_documents_with_metadata()
    
    if documents:
        print("\nExample metadata from the first page:")
        print(documents[0].metadata)
        
        print("\nExample metadata from the last page:")
        print(documents[-1].metadata)
