import uuid
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from chunking.chunk_models import CodeChunk

# Build language objects
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

LANGUAGE_MAP = {
    ".py": ("python", PY_LANGUAGE),
    ".js": ("javascript", JS_LANGUAGE),
    ".ts": ("javascript", JS_LANGUAGE),  # TS uses JS grammar for basics
}

# Node types to extract as separate chunks
CHUNK_NODE_TYPES = {
    "python": ["function_definition", "class_definition"],
    "javascript": ["function_declaration", "class_declaration", "arrow_function"],
}

def get_parser(extension: str) -> tuple[Parser, str] | None:
    """Returns (parser, language_name) for a given file extension."""
    if extension not in LANGUAGE_MAP:
        return None
    lang_name, lang_obj = LANGUAGE_MAP[extension]
    parser = Parser(lang_obj)
    return parser, lang_name


def extract_chunks_from_file(file_path: str, repo_name: str) -> list[CodeChunk]:
    """
    Parses a single file and returns a list of CodeChunk objects.
    Falls back to whole-file chunk if AST parsing fails.
    """
    extension = Path(file_path).suffix
    result = get_parser(extension)
    
    if result is None:
        return []
    
    parser, lang_name = result
    
    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source_code = f.read()
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return []
    
    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)
    
    chunks = []
    target_types = CHUNK_NODE_TYPES.get(lang_name, [])
    
    # Walk the AST and find function/class nodes
    def walk_tree(node):
        if node.type in target_types:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            chunk_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8")
            
            # Extract the name of the function/class
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "anonymous"
            
            # Relative file path for cleaner metadata
            rel_path = file_path.split(repo_name)[-1].lstrip("/\\")
            
            chunk = CodeChunk(
                chunk_id=f"{rel_path}::{name}::{start_line}",
                content=chunk_text,
                file_path=rel_path,
                chunk_type=node.type.replace("_definition", "").replace("_declaration", ""),
                name=name,
                start_line=start_line,
                end_line=end_line,
                language=lang_name,
                repo_name=repo_name,
            )
            chunks.append(chunk)
        
        for child in node.children:
            walk_tree(child)
    
    walk_tree(tree.root_node)
    
    # Fallback: if no chunks found (e.g. script-level code), use whole file
    if not chunks:
        rel_path = file_path.split(repo_name)[-1].lstrip("/\\")
        chunks.append(CodeChunk(
            chunk_id=f"{rel_path}::module::1",
            content=source_code[:3000],  # Cap at 3000 chars for module-level
            file_path=rel_path,
            chunk_type="module",
            name=Path(file_path).stem,
            start_line=1,
            end_line=source_code.count("\n"),
            language=lang_name,
            repo_name=repo_name,
        ))
    
    return chunks


def chunk_repository(file_paths: list[str], repo_name: str) -> list[CodeChunk]:
    """
    Runs AST chunking over all files in the repo.
    Returns flat list of all CodeChunk objects.
    """
    all_chunks = []
    for fp in file_paths:
        file_chunks = extract_chunks_from_file(fp, repo_name)
        all_chunks.extend(file_chunks)
    
    print(f"Total chunks extracted: {len(all_chunks)}")
    return all_chunks
