import argparse
import logging

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("agentAPI").setLevel(logging.DEBUG)

from agentAPI import OllamaBackend, AnthropicBackend, MistralBackend
from agentAPI import Agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat CLI")
    parser.add_argument("-b", "--backend", type=str, 
                        choices=["ollama", "anthropic", "mistral"],
                        default="ollama",
                        help="choice of backend")
    args = parser.parse_args()
    if args.backend == "ollama":
        ollama_instance = Agent(OllamaBackend())
        ollama_instance.repl()
    elif args.backend == "anthropic":
        anthropic_instance = Agent(AnthropicBackend())
        anthropic_instance.repl()
    elif args.backend == "mistral":
        mistral_instance = Agent(MistralBackend())
        mistral_instance.repl()