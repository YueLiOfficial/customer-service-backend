from pydantic import BaseModel

class ChatObjectPyload(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict

class ChatRequest(BaseModel):
    sender_id: str
    text: str | None = None
    object: ChatObjectPyload | None = None
    message_id: str | None = None

class BotMessageResponse(BaseModel):
    text: str | None = None
    object: ChatObjectPyload | None = None

class ChatResponse(BaseModel):
    sender_id: str
    messages: list[BotMessageResponse]
    message_id: str | None = None

class HistoryMessageResponse(BaseModel):
    role: str
    text: str | None = None
    object: ChatObjectPyload | None = None

class ChatHistoryResponse(BaseModel):
    sender_id: str
    messages: list[HistoryMessageResponse]