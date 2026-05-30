from typing import Any, Protocol, cast
from dotenv import load_dotenv
import logging

import anthropic
from anthropic.types import MessageParam, TextBlock

from .backend import (ChatResult, Message,
                      BackendConnectionError, BackendResponseError,
                      BackendContractError)


logger = logging.getLogger(__name__)

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
            messages: list[Message],
            *,
            system: str | None = None) -> ChatResult:
        if system is None:
            system = self.system_prompt
        try:
            logger.debug("Attempting connection with anthropic")
            response = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=cast(list[MessageParam], messages),
                system=system,
            )
            block = response.content[0]
            logger.debug(
                "Response received from anthropic, "
                "Tokens in: %d, Tokens out: %d",
                response.usage.input_tokens, response.usage.output_tokens)
            if not isinstance(block, TextBlock):
                raise BackendContractError(
                    f"Expected a single text response, got "
                    f"{type(block)}")
            else:
                return ChatResult(content=block.text,
                            tokens_in=response.usage.input_tokens,
                            tokens_out=response.usage.output_tokens)
        except anthropic.APIConnectionError as e:
            raise BackendConnectionError(
                f"Could not reach Anthropic : {str(e)}") from e
