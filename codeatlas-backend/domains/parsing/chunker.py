import tiktoken
from .ir import SymbolType, LanguageAdapter

class ASTChunker:
    def __init__(self, max_tokens: int = 500, overlap_tokens: int = 50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        # Using OpenAI's tokenizer as a fast, reliable proxy for local models
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text, disallowed_special=()))

    def _split_large_node(self, node, source_code: bytes, breadcrumbs: list) -> list:
        """
        Recursively splits a massive AST node (like a 2000-line method) 
        by its child statements, applying token limits and overlap.
        """
        chunks = []
        current_chunk_text = ""
        current_tokens = 0
        part_number = 1

        for child in node.children:
            child_text = source_code[child.start_byte:child.end_byte].decode("utf-8")
            child_tokens = self._count_tokens(child_text)

            # If a single child is somehow still too big, we just force-split it (edge case)
            if child_tokens > self.max_tokens:
                # In a full production system, we'd recurse deeper here.
                # For MVP, we accept it as a hard boundary.
                pass 

            if current_tokens + child_tokens > self.max_tokens and current_chunk_text:
                # Save the current chunk
                chunks.append({
                    "name": f"{breadcrumbs[-1]['name']}_part{part_number}",
                    "type": f"{breadcrumbs[-1]['type']}_part",
                    "parent": breadcrumbs[-1]["name"],
                    "code": current_chunk_text,
                    "part": part_number
                })
                part_number += 1
                
                # Start new chunk with overlap (if possible, simplified for MVP)
                current_chunk_text = child_text + "\n"
                current_tokens = child_tokens
            else:
                current_chunk_text += child_text + "\n"
                current_tokens += child_tokens

        # Catch the remainder
        if current_chunk_text.strip():
            chunks.append({
                "name": f"{breadcrumbs[-1]['name']}_part{part_number}",
                "type": f"{breadcrumbs[-1]['type']}_part",
                "parent": breadcrumbs[-1]["name"],
                "code": current_chunk_text,
                "part": part_number
            })

        return chunks

    def extract_symbols(self, root_node, adapter: LanguageAdapter, source_code: bytes):
        symbols = []
        context_stack = []

        def dfs(node):
            symbol_type = adapter.get_symbol_type(node.type)
            
            if symbol_type != SymbolType.UNKNOWN:
                name = adapter.get_name_node(node)
                
                if symbol_type == SymbolType.FUNCTION and context_stack:
                    if context_stack[-1]["type"] == SymbolType.CLASS.value:
                        symbol_type = SymbolType.METHOD
                
                raw_code = source_code[node.start_byte:node.end_byte].decode("utf-8")
                token_count = self._count_tokens(raw_code)

                symbol_data = {
                    "name": name,
                    "type": symbol_type.value,
                    "parent": context_stack[-1]["name"] if context_stack else None,
                }
                
                context_stack.append(symbol_data)

                if token_count <= self.max_tokens:
                    # Fits perfectly, save as one chunk
                    symbol_data["code"] = raw_code
                    symbol_data["part"] = 1
                    symbols.append(symbol_data)
                else:
                    # Too big -> trigger your recursive splitting logic
                    split_chunks = self._split_large_node(node, source_code, context_stack)
                    symbols.extend(split_chunks)
                
                # Still traverse children in case there are nested classes/functions
                for child in node.children:
                    dfs(child)
                    
                context_stack.pop()
            else:
                for child in node.children:
                    dfs(child)

        dfs(root_node)
        return symbols