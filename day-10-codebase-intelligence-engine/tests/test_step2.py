import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from chunking.ast_chunker import extract_chunks_from_file
import tempfile

def test_ast_chunking():
    print("\n[STEP 2] Testing Step 2: AST-Aware Chunking")
    print("-" * 40)
    
    # Create a dummy python file
    code = """
def hello_world():
    print("Hello, world!")

class MyClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        print(f"Hello, {self.name}!")

# Script level code
x = 10
print(x)
"""
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    
    try:
        repo_name = "test_repo"
        chunks = extract_chunks_from_file(tmp_path, repo_name)
        
        print(f"OK: Extracted {len(chunks)} chunks from sample Python file.")
        
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}: {chunk.name} ({chunk.chunk_type}) | Lines {chunk.start_line}-{chunk.end_line}")
        
        # We expect: hello_world, MyClass
        # Note: In the current implementation, MyClass will be a chunk, 
        # but what about functions inside classes? 
        # CHUNK_NODE_TYPES = {"python": ["function_definition", "class_definition"]}
        # In the walk_tree, it descends into children. 
        # So it should find both.
        
        chunk_names = [c.name for c in chunks]
        assert "hello_world" in chunk_names
        assert "MyClass" in chunk_names
        assert "__init__" in chunk_names
        assert "greet" in chunk_names
        
        print("OK: All expected function/class chunks found!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            print("🧹 Cleanup done.")

if __name__ == "__main__":
    test_ast_chunking()
