
from langchain.chat_models import init_chat_model

from app.conf.config import settings


llm = init_chat_model(
    model=settings.llm_model,
    model_provider="openai",
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    temperature=0,
    extra_body={
        "enable_thinking": False
    }
)

if __name__ == "__main__":
    res = llm.invoke("你好")
    print(res.content)