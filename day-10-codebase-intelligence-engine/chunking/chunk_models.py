from pydantic import BaseModel
from typing import Optional

class CodeChunk(BaseModel):
    chunk_id: str               # Unique ID: filepath_functionname_startline
    content: str                # Actual code text
    file_path: str              # e.g. "src/auth/login.py"
    chunk_type: str             # "function", "class", "module"
    name: str                   # Function or class name
    start_line: int
    end_line: int
    language: str               # "python", "javascript", etc.
    repo_name: str
