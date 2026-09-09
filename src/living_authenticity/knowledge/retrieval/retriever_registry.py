from .base_retriever import KnowledgeRetriever
from .token_overlap import DefaultRetriever


class RetrieverRegistry:
    """Hold named knowledge-unit retrievers.

    The default token-overlap retriever is always available. Additional
    retrievers may be registered under distinct names.
    """

    def __init__(self, name: str = "default", retriever: KnowledgeRetriever | None = None) -> None:
        self._name = name
        self._retrievers = {name: retriever if retriever is not None else DefaultRetriever()}

    def register(self, name: str, retriever: KnowledgeRetriever) -> None:
        if name in self._retrievers:
            raise ValueError(f"a retriever named '{name}' is already registered")
        self._retrievers[name] = retriever

    def get(self, name: str):
        if name not in self._retrievers:
            raise ValueError(f"no retriever registered under '{name}'")
        retriever = self._retrievers[name]
        if retriever is None:
            raise ValueError(f"retriever '{name}' has not been provided")
        return retriever

    def default(self):
        return self.get(self._name)
