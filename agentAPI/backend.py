from dataclasses import dataclass 

@dataclass(frozen=True)
class ChatResult:
    content: str
    tokens_in: int
    tokens_out: int

class BackendError(Exception): pass
class BackendConnectionError(BackendError): pass
class BackendResponseError(BackendError): pass
