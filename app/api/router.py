import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_dialogue_service, get_history_service
from app.api.schemas import BotMessageResponse, ChatHistoryResponse, ChatObjectPyload, ChatRequest, ChatResponse, HistoryMessageResponse
from app.domain.messages import MessageObject, MessageType, ProcessMessage, UserMessage
from app.service.dialogue_service import DialogueService
from app.service.history_service import HistoryService

router = APIRouter()

@router.get("/api/chat/history", response_model=ChatHistoryResponse)
async def chat_history(sender_id: str, service: HistoryService = Depends(get_history_service)):
    turns = await service.build_history_turns(sender_id)

    messages: list[HistoryMessageResponse] = []

    for turn in turns:
        usermessage = turn.input_message
        messages.append(
            HistoryMessageResponse(
                role="user",
                text=usermessage.text,
                object=ChatObjectPyload(**usermessage.object.to_dict()) if usermessage.object else None
            )
        )

        bot_messages = turn.assistant_message
        for bot_msg in bot_messages:
            messages.append(
                HistoryMessageResponse(
                    role="bot",
                    text=bot_msg.text,
                    object=ChatObjectPyload(**bot_msg.object.to_dict()) if bot_msg.object else None
                )
            )

    return ChatHistoryResponse(
        sender_id=sender_id,
        messages=messages
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