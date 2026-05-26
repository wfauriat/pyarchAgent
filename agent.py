import httpx
from typing import List

MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

def chat(messages: List[dict]) -> str:
    """
    Send message to the local Ollama model and returns 
    the assistant reply
    """
    payload = {"model": MODEL,
               "stream": False,
               "think": False,
               "messages": messages
    }
    # Error handling needs work
    try:
        response = httpx.post(
            OLLAMA_URL,
            json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Recived: {response.status_code}"
    except BaseException as e:
        return str(e)


if __name__ == "__main__":
    messages = [
    {"role": "user",
    "content": "Why is the sky blue? Answer briefly without thinking."}
            ]
    print(chat(messages))

