import sys
import os
from pathlib import Path

# Add the parent directory to sys.path so we can import from the root
sys.path.append(str(Path(__file__).parent.parent))

import shutil
import stat
from ingestion.github_loader import clone_repo, get_repo_name, walk_code_files
from config import SUPPORTED_EXTENSIONS

def on_rm_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree on Windows.
    Handles read-only files (common in .git folders).
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Failed to delete {path}: {e}")

def test_github_loader():
    # Using a simple repo for testing
    test_repo_url = "https://github.com/octocat/Spoon-Knife"
    target_dir = "./tmp_test_repo"
    
    print("\n[STEP 1] Testing Step 1: GitHub Ingestion")
    print("-" * 40)
    print(f"Supported Extensions (from config.py): {SUPPORTED_EXTENSIONS}")
    
    # Test 1: get_repo_name
    repo_name = get_repo_name(test_repo_url)
    print(f"OK: Extracted Repo Name: {repo_name}")
    assert repo_name == "Spoon-Knife", f"Expected Spoon-Knife, got {repo_name}"
    
    # Test 2: clone_repo
    try:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, onerror=on_rm_error)
            
        cloned_path = clone_repo(test_repo_url, target_dir)
        print(f"OK: Cloned Path: {cloned_path}")
        assert os.path.exists(cloned_path), "Cloned path does not exist"
        assert os.path.isdir(cloned_path), "Cloned path is not a directory"
        
        # Test 3: walk_code_files
        # Note: Spoon-Knife has index.html, styles.css which are NOT in our default SUPPORTED_EXTENSIONS
        # default: [".py", ".js", ".ts", ".java", ".go", ".rs"]
        files = walk_code_files(cloned_path)
        print(f"OK: Found {len(files)} code files matching extensions.")
        
        # If we want to verify it works, we should see 0 files for Spoon-Knife 
        # unless we add .html to extensions temporarily or test a py repo.
        if not files:
            print("ℹ️ Note: No code files found. This is expected as Spoon-Knife doesn't have .py, .js, etc.")
        else:
            print(f"Files found: {files}")
            
    except Exception as e:
        print(f"ERROR: Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, onerror=on_rm_error)
            print("Cleanup done.")

if __name__ == "__main__":
    test_github_loader()
