import os
import shutil
from pathlib import Path
from git import Repo
from config import SUPPORTED_EXTENSIONS

def on_rm_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    Handles read-only files (common on Windows with .git folder).
    """
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url: str, target_dir: str = "./tmp_repo") -> str:
    """
    Clones a GitHub repo to a local directory.
    Returns the path to the cloned repo.
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, onerror=on_rm_error)  # Clean up any previous clone
    
    print(f"Cloning {repo_url}...")
    Repo.clone_from(repo_url, target_dir)
    print(f"Cloned to {target_dir}")
    return target_dir


def get_repo_name(repo_url: str) -> str:
    """Extracts repo name from URL. e.g. 'langchain' from full URL."""
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")


def walk_code_files(repo_path: str) -> list[str]:
    """
    Recursively walks repo directory.
    Returns list of file paths with supported extensions only.
    Skips: node_modules, __pycache__, .git, dist, build
    """
    SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist", "build", ".venv", "venv"}
    code_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Remove skip directories in-place so os.walk doesn't descend into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            ext = Path(file).suffix
            if ext in SUPPORTED_EXTENSIONS:
                full_path = os.path.join(root, file)
                code_files.append(full_path)
    
    print(f"Found {len(code_files)} code files")
    return code_files
