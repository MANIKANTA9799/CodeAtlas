class GitSemanticFormatter:
    """
    Transforms raw Git commit metadata and diffs into semantic, 
    natural-language documents optimized for embedding models.
    """

    @staticmethod
    def format_commit_for_embedding(commit_data: dict) -> str:
        """
        Constructs a human-readable engineering summary of a file-level commit change.
        We strictly use available data to prevent hallucinated summaries.
        """
        hash_id = commit_data.get("commit_hash", "Unknown")
        author = commit_data.get("author", "Unknown")
        date = commit_data.get("date_iso", "Unknown Date")
        message = commit_data.get("message", "No commit message provided.")
        file_path = commit_data.get("file_path", "Unknown File")
        diff = commit_data.get("diff_content", "")

        # Constructing the semantic document based on your exact architectural design
        semantic_text = f"""Commit {hash_id} by {author} on {date}.

This commit modified the file: {file_path}.

Commit message:
{message}

Code changes (Diff):
{diff}

Technical context:
This change represents a historical modification to the repository's evolution. 
The developer modified {file_path} to address the requirements stated in the commit message: '{message}'.
"""
        return semantic_text