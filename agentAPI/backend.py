from dataclasses import dataclass 
from typing import Protocol, TypedDict, Literal

@dataclass(frozen=True)
class ChatResult:
    content: str
    tokens_in: int
    tokens_out: int

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
    
