
import asyncio

from httpx import AsyncClient


http_client: AsyncClient | None = None

def init_http_client():
    global http_client
    http_client = AsyncClient()

async def close_http_client():
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None

if __name__ == "__main__":
    async def main():
        init_http_client()

        assert http_client
        response = await http_client.get("https://www.baidu.com")
        print(response.status_code)

        await close_http_client()

    asyncio.run(main())