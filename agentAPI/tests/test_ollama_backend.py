from agentAPI.ollama_backend import chat

class FakeResponse():
    def raise_for_status(self): pass
    def json(self):
        return {
            "message": {"content": "hi"},
            "prompt_eval_count": 12,
            "eval_count": 4
            }

class FakeClient():
    def post(self, url=None, **kwargs):
        fake_response = FakeResponse()
        return fake_response

def test_chat_parses_successful_response():
    client = FakeClient()
    reply = chat(messages=[{"role": "user", "content": "hello"}], client=client)
    assert reply.content == "hi", f"Expected 'hi', got {reply.content!r}"
    assert reply.tokens_in == 12, f"Expected 12, got {reply.tokens_in!r}"
    assert reply.tokens_out == 4, f"Expected 4, got {reply.tokens_out!r}"
