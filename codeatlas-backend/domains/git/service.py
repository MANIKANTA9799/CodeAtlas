import time
from pathlib import Path
from typing import Iterator, Dict, Any
import git
from git.exc import InvalidGitRepositoryError

class GitHistoryScanner:
    """
    Extracts commit history and file-level diffs from a local Git repository.
    Designed as a generator to maintain O(1) memory complexity regardless of repository size.
    """

    def __init__(self, repo_path: str | Path, max_diff_length: int = 4000):
        self.repo_path = Path(repo_path).resolve()
        self.max_diff_length = max_diff_length
        
        try:
            self.repo = git.Repo(self.repo_path)
        except InvalidGitRepositoryError:
            raise ValueError(f"Path is not a valid Git repository: {self.repo_path}")

    def _sanitize_text(self, text: bytes | str | None) -> str:
        """Decodes raw Git bytes to UTF-8, replacing invalid characters."""
        if not text:
            return ""
        if isinstance(text, bytes):
            return text.decode("utf-8", errors="replace")
        return str(text)

    def scan_commits(self, max_commits: int = 500) -> Iterator[Dict[str, Any]]:
        """
        Iterates through the repository's commit history.
        Yields a dictionary for every file modified in each commit.
        
        Limits to max_commits for MVP performance.
        """
        if self.repo.bare:
            return

        # Iterate through the commit history starting from the active branch (HEAD)
        for commit in self.repo.iter_commits('HEAD', max_count=max_commits):
            parents = commit.parents
            
            # If there are no parents, this is the initial commit. 
            # We skip diffing the initial commit to avoid massive full-repo diffs.
            if not parents:
                continue
                
            parent = parents[0]
            
            # create_patch=True ensures we get the actual +/- lines of code
            diffs = parent.diff(commit, create_patch=True)
            
            for diff in diffs:
                # We only care about files that were added, modified, or renamed
                file_path = diff.b_path if diff.b_path else diff.a_path
                
                # We skip binary files or files without a valid path
                if not file_path:
                    continue
                    
                raw_patch = self._sanitize_text(diff.diff)
                
                # Hard limit on diff size to prevent embedding model token overflow
                if len(raw_patch) > self.max_diff_length:
                    raw_patch = raw_patch[:self.max_diff_length] + "\n... [DIFF TRUNCATED]"

                # Format the ISO time for LLM readability
                commit_time = time.gmtime(commit.committed_date)
                date_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", commit_time)

                yield {
                    "document_type": "commit",
                    "commit_hash": commit.hexsha,
                    "author": commit.author.name,
                    "timestamp": commit.committed_date,
                    "date_iso": date_iso,
                    "message": self._sanitize_text(commit.message).strip(),
                    "file_path": file_path,
                    "diff_content": raw_patch
                }