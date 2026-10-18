import uuid

from fastapi import APIRouter

from app.api.schemas import BotMessageResponse, ChatHistoryResponse, ChatRequest, ChatResponse, HistoryMessageResponse

router = APIRouter()

@router.get("/api/chat/history", response_model=ChatHistoryResponse)
async def chat_history(sender_id: str):
    # TODO: 调用service层获取聊天记录

    return ChatHistoryResponse(
        sender_id=sender_id,
        messages=[
            HistoryMessageResponse(
                role="user",
                text="你好",
            ),
            HistoryMessageResponse(
                role="bot",
                text="你好, 需要什么帮助"
            )
        ]
    )

@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # TODO: 调用service层处理对话

    return ChatResponse(
        sender_id=request.sender_id,
        message_id=request.message_id if request.message_id else str(uuid.uuid4()),
        messages=[
            BotMessageResponse(
                text="你好呀"
            )
        ]
    )