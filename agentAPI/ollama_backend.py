from typing import Any, Protocol

import httpx

from .backend import (ChatResult, Message,
                      BackendConnectionError, BackendResponseError)

class _Response(Protocol):
    def raise_for_status(self) -> Any: ...
    def json(self) -> Any: ...

class _HttpClient(Protocol):
    def post(self,
    url: str, *, json: Any, timeout: float) -> _Response: ...

DEFAULT_SYSTEM = (
    "you are a helpful assistant that answers questions and"
    " provides information. Answer like a pirate."
)

class OllamaBackend():
    def __init__(self, *,
                 system_prompt: str | None = None,
                 client: _HttpClient | None = None):
        self._url = "http://localhost:11434/api/chat"
        self._model = "qwen3:8b"
        self._think = False
        self._request_timeout = 60
        self.system_prompt = system_prompt or DEFAULT_SYSTEM
        self.client = client or httpx.Client()

    def call_model(self,
        messages: list[Message],
        *,
        system: str | None = None,
    ) -> ChatResult:
        """
        Send messages to the local Ollama model and return the 
        assistant reply

        Returns:
            ChatResult: frozen dataclass (content, tokens_in, tokens_out).

        Raises:
            BackendConnectionError: transport failed (couldn't reach Ollama).
            BackendResponseError: Ollama returned a non-2xx status.
        """
        if system is None: system = self.system_prompt
        payload = {
            "model": self._model,
            "stream": False,
            "think": self._think,
            "messages": [{"role": "system",
                          "content": system}, *messages],
        }

        try:
            response = self.client.post(self._url, json=payload,
                                    timeout=self._request_timeout)
            response.raise_for_status()
            data = response.json()
            return ChatResult(content=data["message"]["content"],
                            tokens_in=data["prompt_eval_count"],
                            tokens_out=data["eval_count"])
        except httpx.HTTPStatusError as e:
            raise BackendResponseError(
                f"Ollama returned HTTP {e.response.status_code}: "
                f"{e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise BackendConnectionError(
                f"Could not reach Ollama at {self._url}") from e
