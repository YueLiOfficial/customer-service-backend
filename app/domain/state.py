from dataclasses import dataclass, field
import time

from app.domain.contexts import SystemContext, TaskContext
from app.domain.messages import MessageObject, UserMessage, BotMessage

@dataclass(slots=True)
class Turn:
    turn_id: str
    input_messsage: UserMessage
    assistant_message: list[BotMessage] = field(default_factory=list)

@dataclass(slots=True)
class Session:
    session_id: str
    started_at: float = field(default_factory=time.time)
    last_activity_at: float = field(default_factory=time.time)
    closed_at: float | None = None
    turns: list[Turn] = field(default_factory=list)

@dataclass(slots=True)
class FocusedObject:
    type: str
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)

@dataclass(slots=True)
class DialogueState:
    sender_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_task: SystemContext | None = None
    sessions: list[Session] = field(default_factory=list)
    current_session_id: str | None = None
    focused_object: FocusedObject | None = None
    pending_turn: Turn | None = None