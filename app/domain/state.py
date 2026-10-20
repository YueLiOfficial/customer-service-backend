from dataclasses import asdict, dataclass, field
import time
from typing import Any
import uuid

from app.domain.contexts import SystemContext, TaskContext
from app.domain.messages import MessageObject, UserMessage, BotMessage, ProcessMessage

@dataclass(slots=True)
class Turn:
    turn_id: str
    input_message: UserMessage
    assistant_message: list[BotMessage] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "turn_id": self.turn_id,
            "input_message": self.input_message.to_dict(),
            "assistant_message": [msg.to_dict() for msg in self.assistant_message] 
        }

    @classmethod
    def from_dict(cls, data:dict) -> "Turn":
        ass_mes_list = data.get("assistant_message", [])

        return cls(
            turn_id=data["turn_id"],
            input_message=UserMessage.from_dict(data["input_message"]),
            assistant_message=[BotMessage.from_dict(msg) for msg in ass_mes_list]
        )

@dataclass(slots=True)
class Session:
    session_id: str
    started_at: float = field(default_factory=time.time)
    last_activity_at: float = field(default_factory=time.time)
    closed_at: float | None = None
    turns: list[Turn] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activity_at": self.last_activity_at,
            "closed_at": self.closed_at if self.closed_at else None,
            "turns": [t.to_dict() for t in self.turns]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        turn_list = data.get("turns", [])

        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            last_activity_at=data["last_activity_at"],
            closed_at=data.get("closed_at"),
            turns=[Turn.from_dict(turn) for turn in turn_list]
        )

@dataclass(slots=True)
class FocusedObject:
    type: str
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "FocusedObject":
        return cls(**data)

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

    def get_current_session(self) -> Session | None:
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session
        return None

    def create_session(self) -> None:
        session = Session(
            session_id=str(uuid.uuid4()),
            started_at=time.time(),
            last_activity_at=time.time()
        )

        self.sessions.append(session)
        self.current_session_id = session.session_id

    def close_session(self, session: Session) -> None:
        session.closed_at = time.time()
        self.current_session_id = None

    def clear_state(self) -> None:
        self.active_task = None
        self.paused_tasks = []
        self.active_system_task = None
        self.focused_object = None

    def update_last_active_time(self, session: Session) -> None:
        session.last_activity_at = time.time()

    def create_turn(self, message: UserMessage) -> None:
        turn = Turn(
            turn_id=str(uuid.uuid4()),
            input_message=message
        )
        self.pending_turn = turn

    def fill_turn(self, messages: list[BotMessage]) -> None:
        assert self.pending_turn
        self.pending_turn.assistant_message = messages

    def commit_turn(self, session: Session) -> None:
        assert self.pending_turn
        session.turns.append(self.pending_turn)
        self.pending_turn = None

    def stop_sys_task(self):
        self.active_system_task = None

    def start_sys_task(self, context: SystemContext):
        self.active_system_task = context

    def interrupt_current_task(self):
        assert self.active_task
        self.paused_tasks.append(self.active_task)
        self.active_task = None

    def start_task(self, task_context: TaskContext):
        self.active_task = task_context

    def stop_cur_task(self):
        self.active_task = None
        self.active_system_task = None

    def set_slots(self, slots: dict[str, Any]):
        if self.active_task:
            self.active_task.slots.update(slots)

    def resume_task(self, task_id: str):
        for task in self.paused_tasks:
            if task.flow_id == task_id:
                self.active_task = task
                self.paused_tasks.remove(task)
                break

    def to_dict(self) -> dict:
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [task.to_dict() for task in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "sessions": [s.to_dict() for s in self.sessions],
            "current_session_id": self.current_session_id,
            "focused_object": self.focused_object.to_dict() if self.focused_object else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueState":
        paused_task_list = data.get("paused_tasks")
        session_list = data.get("sessions")
        
        return cls(
            sender_id=data["sender_id"],
            active_task=TaskContext.from_dict(data["active_task"]) if data.get("active_task") else None,
            paused_tasks=[TaskContext.from_dict(task) for task in paused_task_list] if paused_task_list else [],
            active_system_task=SystemContext.from_dict(data["active_system_task"]) if data.get("active_system_task") else None,
            sessions=[
                Session.from_dict(session) for session in session_list
            ] if session_list else [],
            current_session_id=data.get("current_session_id"),
            focused_object=FocusedObject.from_dict(data["focused_object"]) if data.get("focused_object") else None
        )