import anthropic

from dotenv import load_dotenv

from .backend import (
        ChatResult,
    )

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
REQUEST_TIMEOUT = 60  # seconds

PROMPT_SYSTEM = (
    "you are a helpful assistant that answers questions and"
    " provides information. Answer like a pirate."
)

def chat(
    messages: list[dict],
    *,
    model: str = MODEL,
    system: str | None = None,
    max_tokens: int = MAX_TOKENS,
    client: anthropic.Anthropic | None = None,
    ) -> ChatResult:

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system is not None:
        kwargs["system"] = system
    if client is None:
        client = anthropic.Anthropic()
    response = client.messages.create(**kwargs)
    return ChatResult(content=response.content[0].text,
                      tokens_in=response.usage.input_tokens,
                      tokens_out=response.usage.output_tokens)

if __name__ == "__main__":
    load_dotenv()
    anthropic_client = anthropic.Anthropic()
    message = [{"role": "user", 
                "content":"hello who are you ? anwser briefly"}]
    reply = chat(message, system=PROMPT_SYSTEM,
                 client=anthropic_client)
    print(reply.content)

