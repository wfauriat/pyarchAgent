#!/usr/bin/env python3
"""Probe how a model would handle an instruction — WITHOUT executing anything.

Drives the real Agent loop with a deny-all approval policy, so every bash
command the model proposes is refused. Because each refusal is fed back as a
tool result, the model re-plans, and we get to watch its *intent* unfold:
the first plan plus any backup proposals it falls back to — all with nothing
ever touching the disk.

Usage:
    python probe_bash.py "Delete every .pyc file in this project."
    python probe_bash.py -b ollama -r 4 "Free up disk space here."

This is a diagnostic, not part of the package: it imports agentAPI and reuses
Agent.run(), so it exercises the same loop the REPL does.
"""

import argparse
import sys

from agentAPI import Agent, OllamaBackend, AnthropicBackend, MistralBackend
from agentAPI.backend import (
    UserMessage, AssistantMessage, ToolCall, StopReason, BackendError,
)

BACKENDS = {
    "ollama": OllamaBackend,
    "anthropic": AnthropicBackend,
    "mistral": MistralBackend,
}


def deny_all(_: ToolCall) -> bool:
    """Approval policy that never approves — guarantees nothing executes."""
    return False


def _format_call(tc: ToolCall) -> str:
    args = ", ".join(f"{k}={v!r}" for k, v in tc.arguments.items())
    return f"{tc.name}({args})"


def _proposals(transcript: list) -> list[tuple[ToolCall, ...]]:
    """One entry per round in which the model asked for tools, in order."""
    return [m.tool_calls for m in transcript
            if isinstance(m, AssistantMessage) and m.tool_calls]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run probe: see what bash a model WOULD run, run nothing.")
    parser.add_argument("prompt", help="instruction to probe the model with")
    parser.add_argument("-b", "--backend", choices=list(BACKENDS),
                        default="ollama", help="backend (default: ollama)")
    parser.add_argument("-r", "--max-rounds", type=int, default=3,
                        help="how many re-plan rounds to observe (default: 3)")
    args = parser.parse_args()

    agent = Agent(BACKENDS[args.backend](), approve=deny_all,
                  max_rounds=args.max_rounds)

    print(f"probing via {args.backend} (deny-all, up to {args.max_rounds} "
          f"rounds, nothing executed)…", file=sys.stderr)

    transcript: list = [UserMessage(content=args.prompt)]
    try:
        result = agent.run(transcript)
    except BackendError as e:
        print(f"backend error: {e}", file=sys.stderr)
        return 1

    rounds = _proposals(transcript)

    print("=" * 70)
    print(" probe_bash — DRY RUN (deny-all; nothing was executed)")
    print("=" * 70)
    print(f"prompt : {args.prompt}")
    print(f"backend: {args.backend}\n")

    if not rounds:
        print("The model proposed no command; it answered directly.\n")
    for i, calls in enumerate(rounds, start=1):
        label = "first plan" if i == 1 else "backup"
        print(f"-> round {i} ({label})")
        for tc in calls:
            print(f"     {_format_call(tc)}")
        print("     [DENIED]\n")

    print("-- model's final reply " + "-" * 47)
    print(result.content.strip() or "(no text — model was still asking for tools)")

    n_calls = sum(len(c) for c in rounds)
    hit_cap = result.stop_reason == StopReason.TOOL
    print("\n-- summary " + "-" * 59)
    print(f"commands proposed : {n_calls}   |   executed : 0")
    print("stopped because   : " + (
        f"reached max-rounds ({args.max_rounds}) while still wanting tools"
        if hit_cap else "model stopped requesting tools"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
