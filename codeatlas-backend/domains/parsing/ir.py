from enum import Enum
from typing import Dict

class SymbolType(Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    UNKNOWN = "unknown"

class LanguageAdapter:
    def get_symbol_type(self, node_type: str) -> SymbolType:
        raise NotImplementedError

    def get_name_node(self, node) -> str | None:
        raise NotImplementedError

class PythonAdapter(LanguageAdapter):
    def __init__(self):
        self._type_map: Dict[str, SymbolType] = {
            "class_definition": SymbolType.CLASS,
            "function_definition": SymbolType.FUNCTION,
        }

    def get_symbol_type(self, node_type: str) -> SymbolType:
        return self._type_map.get(node_type, SymbolType.UNKNOWN)

    def get_name_node(self, node) -> str | None:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None