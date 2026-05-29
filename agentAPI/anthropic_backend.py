from dotenv import load_dotenv
import anthropic

from .backend import (ChatResult,
                      BackendConnectionError, BackendResponseError)


DEFAULT_SYSTEM = (
    "you are a helpful assistant that answers questions and"
    " provides information."
)

class AnthropicBackend():
    def __init__(self,
            system_prompt: str | None = None,
            *,
            client: anthropic.Anthropic | None = None) -> None:
        self._model = "claude-haiku-4-5-20251001"
        self._max_tokens = 1024
        self.system_prompt = system_prompt or DEFAULT_SYSTEM
        if client is None:
            load_dotenv()
            self.client = anthropic.Anthropic()
        else: self.client = client

    def call_model(self,
            messages: list[dict],
            ) -> ChatResult:
        kwargs = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": messages,
            "system": self.system_prompt
        }
        try:
            response = self.client.messages.create(**kwargs)
            return ChatResult(content=response.content[0].text,
                            tokens_in=response.usage.input_tokens,
                            tokens_out=response.usage.output_tokens)
        except anthropic.APIConnectionError as e:
            raise BackendConnectionError(
                f"Could not reach Anthropic : {str(e)}") from e