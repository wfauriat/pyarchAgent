import httpx
from .backend import (
        ChatResult,
        BackendError,
        BackendConnectionError,
        BackendResponseError
    )


MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"
REQUEST_TIMEOUT = 60  # seconds

PROMPT_SYSTEM = (
    "you are a helpful assistant that answers questions and"
    " provides information. Answer like a pirate."
)


def chat(
    messages: list[dict],
    *,
    model: str = MODEL,
    url: str = OLLAMA_URL,
    timeout: float = REQUEST_TIMEOUT,
    client: httpx.Client | None = None,
    think: bool = False,
) -> ChatResult:
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
        raise BackendConnectionError(f"Could not reach Ollama at {url}") from e


def main() -> None:

    messages: list[dict] = []
    messages.append({"role":"system", "content":PROMPT_SYSTEM})
    with httpx.Client() as client:
        while True:
            print("="*80)
            print("User:")
            print("="*80)
            try:
                prompt = input("> ")
                if prompt.strip().lower() == "quit" or prompt == "/quit":
                    print("\nbye")
                    break
                user_msg = {"role":"user", "content":prompt}
                reply = chat(messages=[*messages, user_msg], client=client)
                messages.append(user_msg)
                messages.append({"role":"assistant", "content":reply.content})
                print("\n", "="*80)
                print("Assistant:")
                print("="*80)
                print(reply.content, "\n")
                print(f"tokens_in: {reply.tokens_in}, "
                      f"tokens_out: {reply.tokens_out}")
            except (KeyboardInterrupt, EOFError):
                print("\nbye")
                break

if __name__ == "__main__":
    main()
