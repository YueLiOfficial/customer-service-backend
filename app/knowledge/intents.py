from dataclasses import dataclass

@dataclass(slots=True)
class KnowledgeIntent:
    id_: str
    description: str
    provider_ids: list[str]
    requires_object: str | None = None

KNOWLEDGE_INTENTS = {
    "product_info": KnowledgeIntent(
        id_="product_info",
        description="商品信息查询",
        provider_ids=["api.product"],
        requires_object="product"
    ),
    "order_info": KnowledgeIntent(
        id_="order_info",
        description="订单详情查询",
        provider_ids=["api.order"],
        requires_object="order"
    ),
    "price_protected_policy": KnowledgeIntent(
        id_="price_protected_policy",
        description="保价政策咨询",
        provider_ids=["rag.default"]
    ),
    "refund_policy": KnowledgeIntent(
        id_="refund_policy",
        description="退款政策咨询",
        provider_ids=["rag.default"]
    ),
    "faq_question": KnowledgeIntent(
        id_="faq_question",
        description="电商FAQ问题查询",
        provider_ids=["faq.default"]
    )
}