from dataclasses import dataclass 
from typing import Any, Protocol, TypedDict, Literal
from enum import Enum

@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

class StopReason(Enum):
    END = "end"
    TOOL = "tool"
    MAX_TOKENS = "max_tokens"

@dataclass(frozen=True, kw_only=True)
class ChatResult:
    stop_reason: StopReason
    content: str
    tokens_in: int
    tokens_out: int
    tool_calls: tuple[ToolCall, ...] = ()

class BackendError(Exception): pass
class BackendConnectionError(BackendError): pass
class BackendResponseError(BackendError): pass
class BackendContractError(BackendError): pass

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class Backend(Protocol):
    def call_model(self,
        messages: list[Message],
        *,
        system: str | None = None
        ) -> ChatResult: ...
    
