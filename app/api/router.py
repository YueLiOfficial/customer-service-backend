import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_dialogue_service
from app.api.schemas import BotMessageResponse, ChatHistoryResponse, ChatObjectPyload, ChatRequest, ChatResponse, HistoryMessageResponse
from app.domain.messages import MessageObject, MessageType, ProcessMessage, UserMessage
from app.service.dialogue_service import DialogueService

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
async def chat(request: ChatRequest, service: DialogueService = Depends(get_dialogue_service)):
    user_message = _build_user_message(request)
    
    process_message: ProcessMessage = await service.process_message(user_message)

    return _build_chat_response(process_message)

def _build_user_message(request: ChatRequest) -> UserMessage:
    return UserMessage(
        sender_id=request.sender_id,
        message_id=request.message_id if request.message_id else str(uuid.uuid4()),
        type=MessageType.TEXT if request.text else MessageType.OBJECT,
        text=request.text,
        object=MessageObject(
            type=request.object.type,
            id=request.object.id,
            title=request.object.title,
            attributes=request.object.attributes
        ) if request.object else None
    )

def _build_chat_response(process_message: ProcessMessage) -> ChatResponse:
    return ChatResponse(
        sender_id=process_message.sender_id,
        message_id=process_message.message_id,
        messages=[BotMessageResponse(
            text=bot_message.text,
            object=ChatObjectPyload(**bot_message.object.to_dict()) if bot_message.object else None
        ) for bot_message in process_message.messages]
    )