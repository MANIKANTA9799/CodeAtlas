import os
from pathlib import Path
from typing import Iterator, List
import pathspec

class RepositoryScanner:
    """
    Scans a local directory and yields file paths that should be indexed,
    respecting .gitignore rules and skipping binary/hidden files.
    """
    
    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        
        if not self.repo_path.exists() or not self.repo_path.is_dir():
            raise ValueError(f"Invalid repository path: {self.repo_path}")
            
        self.ignore_spec = self._load_gitignore()
        
        # Hardcoded directories we ALWAYS ignore, even if not in .gitignore
        self.always_ignore_dirs = {
            ".git", ".idea", ".vscode", 
            "venv", "env", ".venv", "atlas"
        }

    def _load_gitignore(self) -> pathspec.PathSpec:
        """Reads .gitignore and compiles it into a PathSpec object."""
        gitignore_path = self.repo_path / ".gitignore"
        lines: List[str] = []
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                lines = f.readlines()              
        # We use the GitWildMatchPattern to perfectly mimic Git's behavior
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, lines) #type:ignore

    def _is_text_file(self, filepath: Path) -> bool:
        """
        Heuristic to check if a file is text or binary.
        Reads the first chunk of bytes and checks for null bytes.
        """
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
            return b'\x00' not in chunk
        except Exception:
            return False

    def scan(self) -> Iterator[Path]:
        """
        Walks the repository and yields valid, non-ignored text files.
        """
        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # 1. Modify 'dirs' in-place to prevent os.walk from entering ignored directories
            # This is a massive performance optimization!
            dirs[:] = [d for d in dirs if d not in self.always_ignore_dirs]
            
            # Calculate the relative path to check against pathspec
            for file_name in files:
                file_path = root_path / file_name
                
                # We check the path relative to the repo root
                relative_path = str(file_path.relative_to(self.repo_path))
                
                # 2. Skip files matched by .gitignore
                if self.ignore_spec.match_file(relative_path):
                    continue
                    
                # 3. Skip binaries (like .png, .pyc, compiled executables)
                if not self._is_text_file(file_path):
                    continue
                    
                yield file_path