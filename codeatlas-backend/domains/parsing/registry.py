import os
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript

class LanguageRegistry:
    def __init__(self):
        self._grammars = {
            ".py": tree_sitter_python.language(),
            ".js": tree_sitter_javascript.language(),
            ".ts": tree_sitter_typescript.language_typescript(),
            ".tsx": tree_sitter_typescript.language_tsx(),
        }
        self._parsers: dict[str, Parser] = {}

    def get_parser(self, filepath: str) -> Parser | None:
        _, extension = os.path.splitext(filepath)
        extension = extension.lower()

        if extension not in self._grammars:
            return None
            
        if extension not in self._parsers:
            # NEW API (v0.22+): Pass Language directly to the Parser constructor
            language = Language(self._grammars[extension])
            parser = Parser(language)
            
            self._parsers[extension] = parser
            
        return self._parsers[extension]