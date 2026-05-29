from dataclasses import dataclass 
from typing import Protocol

@dataclass(frozen=True)
class ChatResult:
    content: str
    tokens_in: int
    tokens_out: int

class BackendError(Exception): pass
class BackendConnectionError(BackendError): pass
class BackendResponseError(BackendError): pass

class Backend(Protocol):
    def call_model(self,
        messages: list[dict],
        *,
        system: str | None = None
        ) -> ChatResult: ...