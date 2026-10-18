from dataclasses import asdict, dataclass, field
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    OBJECT = "object"

@dataclass(slots=True)
class MessageObject:
    type: str
    id: str
    title: str| None = None
    attributes: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data_dict) -> "MessageObject":
        return cls(**data_dict)

@dataclass(slots=True)
class UserMessage:
    sender_id: str
    type: MessageType
    text: str| None = None
    object: MessageObject | None = None
    message_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "sender_id": self.sender_id,
            "type": MessageType(self.type),
            "text": self.text,
            "object": self.object,
            "message_id": self.message_id
        }
    
    @classmethod
    def from_dict(cls, data_dict: dict) -> "UserMessage":
        return cls(
            sender_id=data_dict["sender_id"],
            type=data_dict["type"],
            text=data_dict.get("text"),
            message_id=data_dict.get("message_id"),
            object = MessageObject.from_dict(data_dict.get("object")) if data_dict.get("object") else None
        )

@dataclass(slots=True)
class BotMessage:
    text: str | None = None
    object: MessageObject | None = None

    def to_dict(self):
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None
        }

@dataclass(slots=True)
class ProcessMessage:
    sender_id: str
    messages: list[BotMessage]
    message_id: str | None = None
