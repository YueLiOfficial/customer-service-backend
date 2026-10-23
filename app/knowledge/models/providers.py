from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
import json

from app.domain.state import DialogueState
from app.infra import http_util
from app.conf.config import settings

@dataclass(slots=True)
class KnowledgeChunk:
    content: str

class KnowledgeProvider(ABC):
    provider_id: str = ""

    @abstractmethod
    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        ...

class ProductProvider(KnowledgeProvider):
    provider_id = "api.product"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        if state.focused_object:
            product_id = state.focused_object.id

            assert http_util.http_client is not None
            response = await http_util.http_client.get(f"{settings.commerce_api_base_url}/products/{product_id}")
            if response and response.json().get("code") == 0:
                json_str = json.dumps(response.json().get("data"), ensure_ascii=False, indent=4)
                return [KnowledgeChunk(content=json_str)]
            else:
                return [KnowledgeChunk(content="无法获取商品信息!")]
        else:
            return [KnowledgeChunk(content="请输入商品id")]

class OrderProvider(KnowledgeProvider):
    provider_id = "api.order"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        if state.focused_object:
            order_id = state.focused_object.id

            assert http_util.http_client is not None
            infos, status, logistics = await asyncio.gather(
                self.get_api_response(order_id, f"{settings.commerce_api_base_url}/orders/{order_id}"),
                self.get_api_response(order_id, f"{settings.commerce_api_base_url}/orders/{order_id}/status"),
                self.get_api_response(order_id, f"{settings.commerce_api_base_url}/orders/{order_id}/logistics")
            )

            return [
                KnowledgeChunk(content=f"订单详情: {infos}"),
                KnowledgeChunk(content=f"订单状态: {status}"),
                KnowledgeChunk(content=f"订单物流: {logistics}")
            ]
        else:
            return [KnowledgeChunk(content="请输入订单id")]
    
    async def get_api_response(self, order_id: str, url: str) -> str:
        assert http_util.http_client is not None
        response = await http_util.http_client.get(url)
        if response and response.json().get("code") == 0:
            json_str = json.dumps(response.json().get("data"), ensure_ascii=False, indent=4)
            return json_str
        else:
            return ""

class PolicyProvider(KnowledgeProvider):
    provider_id = "faq.default"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        return [KnowledgeChunk(content="未检索到相关问题（faq）")]

class FAQProvider(KnowledgeProvider):
    provider_id = "rag.default"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        return [KnowledgeChunk(content="未检索到相关问题（rag）")]

if __name__ == '__main__':
    from app.domain.state import FocusedObject
    async def test():
        http_util.init_http_client()
        state = DialogueState(sender_id="u1001")
        state.focused_object = FocusedObject(
            id="SKU10001",
            title="iPhone 11",
            type="product"
        )
        res = await ProductProvider().retrieve(state)
        print(res)

    asyncio.run(test())