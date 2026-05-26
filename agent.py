import httpx

import json

first_message = {"model": "qwen3:8b",
                 "messages": [
                     {"role": "user",
                      "content": "Why is the sky blue? Answer briefly without thinking."}
                 ],
                 "stream": False,
                 "think": False}


response = httpx.post(
    "http://localhost:11434/api/chat",
    json=first_message, timeout=120)

if __name__ == "__main__":
    print(response)
    print(response.status_code)
    print(response.text)

