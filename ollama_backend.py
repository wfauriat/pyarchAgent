import httpx

MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"
REQUEST_TIMEOUT = 60  # seconds

class BackendError(Exception): pass
class BackendConnectionError(BackendError): pass
class BackendResponseError(BackendError): pass

def chat(
    messages: list[dict],
    *,
    model: str = MODEL,
    url: str = OLLAMA_URL,
    timeout: float = REQUEST_TIMEOUT,
    client: httpx.Client | None = None,
    think: bool = False,
) -> str:
    """
    Send messages to the local Ollama model and return the assistant reply.

    Defaults for `model`, `url`, `timeout` come from module-level constants;
    pass keyword overrides to vary them per call. Pass `client` to reuse a
    long-lived `httpx.Client` (connection reuse, shared headers); if omitted,
    a transient client is created for this call only. `think` toggles qwen3's
    thinking mode (ignored by other models / backends).

    Raises:
        BackendConnectionError: transport failed (couldn't reach Ollama).
        BackendResponseError: Ollama returned a non-2xx status.
    """
    payload = {
        "model": model,
        "stream": False,
        "think": think,
        "messages": messages,
    }

    try:
        if client is None:
            response = httpx.post(url, json=payload, timeout=timeout)
        else:
            response = client.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except httpx.HTTPStatusError as e:
        raise BackendResponseError(
            f"Ollama returned HTTP {e.response.status_code}: "
            f"{e.response.text}"
        ) from e
    except httpx.RequestError as e:
        raise BackendConnectionError(f"Could not reach Ollama at {url}") from e


if __name__ == "__main__":
    messages = [
    {"role": "user",
    "content": "Why is the sky blue? Answer briefly without thinking."}
            ]
    print(chat(messages))

