from typing import Any

from app.knowledge.models.providers import KnowledgeProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, Any] = {}

    def register(self, provider: KnowledgeProvider):
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> KnowledgeProvider:
        if provider_id not in self._providers:
            raise KeyError(f"{provider_id} 不存在")
        return self._providers[provider_id]