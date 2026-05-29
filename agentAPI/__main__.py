import argparse

from agentAPI import OllamaBackend, AnthropicBackend
from agentAPI import Backend

def repl(backend: Backend):
    messages: list[dict] = []
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
            reply = backend.call_model(messages=[*messages, user_msg])
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
    parser = argparse.ArgumentParser(description="Chat CLI")
    parser.add_argument("-b", "--backend", type=str, 
                        choices=["ollama", "anthropic"],
                        default="ollama",
                        help="choice of backend")
    args = parser.parse_args()
    if args.backend == "ollama":
        ollama_instance = OllamaBackend()
        repl(ollama_instance)
    elif args.backend == "anthropic":
        anthropic_instance = AnthropicBackend()
        repl(anthropic_instance)