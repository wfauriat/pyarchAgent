from collections import namedtuple

import pytest
import httpx
import anthropic
from anthropic.types import TextBlock

from agentAPI.anthropic_backend import AnthropicBackend
from agentAPI.backend import (Message,
    BackendConnectionError, BackendResponseError)

MOCK_MESSAGE: list[Message] = [{"role": "user", "content": "hello"}]


class FakeMessage():
    def __init__(self, *, create_error=None):
        self._create_error = create_error

    def create(self, **kwargs):
        self.sent_kwargs = kwargs
        if self._create_error:
            raise self._create_error
        Usage = namedtuple("Usage", ["input_tokens", "output_tokens"])
        Response = namedtuple("Response", ["content", "usage"])
        return Response(content=[TextBlock(text="hi", type="text")],
                        usage=Usage(input_tokens=12, output_tokens=4))


class FakeClient():
    def __init__(self, message):
        self.messages = message


def _api_status_error(status_code):
    request = httpx.Request("POST", "http://test")
    response = httpx.Response(status_code, text="server boom",
                             request=request)
    return anthropic.APIStatusError("server boom",
                                    response=response, body=None)


def test_call_model_parses_successful_response():
    backend = AnthropicBackend(client=FakeClient(FakeMessage()))
    reply = backend.call_model(messages=MOCK_MESSAGE)
    assert reply.content == "hi", f"Expected 'hi', got {reply.content!r}"
    assert reply.tokens_in == 12, f"Expected 12, got {reply.tokens_in!r}"
    assert reply.tokens_out == 4, f"Expected 4, got {reply.tokens_out!r}"


def test_call_model_raises_connection_error_when_create_fails():
    request = httpx.Request("POST", "http://test")
    backend = AnthropicBackend(client=FakeClient(
        FakeMessage(create_error=anthropic.APIConnectionError(
            message="boom", request=request))))
    with pytest.raises(BackendConnectionError) as excinfo:
        backend.call_model(messages=MOCK_MESSAGE)
    assert "Could not reach" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, anthropic.APIConnectionError)


@pytest.mark.xfail(
    strict=True,
    reason="protocol layer not implemented: call_model does not yet "
           "translate anthropic.APIStatusError -> BackendResponseError",
)
def test_call_model_raises_response_error_on_api_status_error():
    backend = AnthropicBackend(client=FakeClient(
        FakeMessage(create_error=_api_status_error(429))))
    with pytest.raises(BackendResponseError) as excinfo:
        backend.call_model(messages=MOCK_MESSAGE)
    assert "429" in str(excinfo.value)


def test_call_model_sends_system_and_messages_in_payload():
    # no per-call system -> falls back to the constructor default
    message = FakeMessage()
    backend = AnthropicBackend(system_prompt="be terse",
                               client=FakeClient(message))
    backend.call_model(messages=MOCK_MESSAGE)
    sent = message.sent_kwargs
    assert sent["system"] == "be terse"
    assert sent["messages"] == MOCK_MESSAGE


def test_call_model_per_call_system_overrides_default():
    # default and override differ, so the assertion proves the override won
    message = FakeMessage()
    backend = AnthropicBackend(system_prompt="default sys",
                               client=FakeClient(message))
    backend.call_model(messages=MOCK_MESSAGE, system="be terse")
    sent = message.sent_kwargs
    assert sent["system"] == "be terse"
    assert sent["messages"] == MOCK_MESSAGE
