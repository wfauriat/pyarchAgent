import pytest
import httpx

from agentAPI.ollama_backend import chat
from agentAPI.backend import BackendConnectionError, BackendResponseError

MOCK_MESSAGE = [{"role": "user", "content":"hello"}]

class FakeResponse():
    def __init__(self, *, status_error=None):
        self._status_error = status_error
    def raise_for_status(self): 
        if self._status_error:
            request = httpx.Request("POST", "http://test")
            response = httpx.Response(self._status_error, text="server boom",
                                      request=request)
            http_err = httpx.HTTPStatusError(f"Error {self._status_error}",
                                             request=request,
                                             response=response)
            raise http_err
    def json(self):
        return {
            "message": {"content": "hi"},
            "prompt_eval_count": 12,
            "eval_count": 4
            }

class FakeClient():
    def __init__(self, *, post_error=None, response=None):
        self._post_error = post_error
        self._response = response or FakeResponse()
    def post(self, url=None, **kwargs):
        if self._post_error: raise self._post_error
        return self._response

    

def test_chat_parses_successful_response():
    reply = chat(messages=MOCK_MESSAGE, client=FakeClient())
    assert reply.content == "hi", f"Expected 'hi', got {reply.content!r}"
    assert reply.tokens_in == 12, f"Expected 12, got {reply.tokens_in!r}"
    assert reply.tokens_out == 4, f"Expected 4, got {reply.tokens_out!r}"

def test_chat_raises_connection_error_when_post_fails():
    with pytest.raises(BackendConnectionError) as excinfo:
        chat(messages=MOCK_MESSAGE, 
             client=FakeClient(post_error=httpx.RequestError("boom")))
    assert "Could not reach" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, httpx.RequestError)

def test_chat_raises_status_error_when_response_send_wrong_status():
    with pytest.raises(BackendResponseError) as excinfo:
        chat(messages=MOCK_MESSAGE,
             client=FakeClient(response=FakeResponse(status_error=500)))
    assert "500" in str(excinfo.value)
    assert "server boom" in str(excinfo.value)