from typing import Any, Protocol
from dotenv import load_dotenv
import anthropic

from .backend import (ChatResult,
                      BackendConnectionError, BackendResponseError)


class _Messages(Protocol):
    def create(self, **kwargs: Any) -> Any: ...

class _AnthropicClient(Protocol):
    @property
    def messages(self) -> _Messages: ...

DEFAULT_SYSTEM = (
    "you are a helpful assistant that answers questions and"
    " provides information."
)

class AnthropicBackend():
    def __init__(self,
            system_prompt: str | None = None,
            *,
            client: _AnthropicClient | None = None) -> None:
        self._model = "claude-haiku-4-5-20251001"
        self._max_tokens = 1024
        self.system_prompt = system_prompt or DEFAULT_SYSTEM
        if client is None:
            load_dotenv()
        self.client = client or anthropic.Anthropic()

    def call_model(self,
            messages: list[dict],
            *,
            system: str | None = None) -> ChatResult:
        if system is None:
            system = self.system_prompt
        try:
            response = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=messages,
                system=system,
            )
            return ChatResult(content=response.content[0].text,
                            tokens_in=response.usage.input_tokens,
                            tokens_out=response.usage.output_tokens)
        except anthropic.APIConnectionError as e:
            raise BackendConnectionError(
                f"Could not reach Anthropic : {str(e)}") from e