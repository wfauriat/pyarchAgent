# Session log

Lightweight running notes. Append-only — past entries are history, don't tidy them.

---

### 2026-05-26 — Project setup + first Ollama call

- Created `projects/agentBuilding/` with `CLAUDE.md` (intent + tutor work mode + session-log convention).
- Branched off `main` into `project/agent-building` to keep this work separable in the larger training repo.
- First commit landed. Practiced commit hygiene: subject ≤50 chars, imperative mood, blank line before body — amended once to fix structure.
- **First brick (in progress)**: single HTTP POST to Ollama's `/api/chat` endpoint, no abstractions, hardcoded values.
  - Chose `httpx` over `requests` (matches a future deployment target that uses httpx + OpenAI API + Kerberos).
  - Chose Ollama's *native* API over its OpenAI-compatible endpoint, deliberately — to feel provider variance before designing any wrapper.
- **Bugs hit along the way**:
  - 405 on `/api/chat` in browser → method confusion (GET vs POST). Status-code mental model installed.
  - 400 from server → double JSON encoding: passed `json=json.dumps(dict)` instead of `json=dict`. Learned `httpx`'s `json=` serializes for you.
  - Timeout → httpx default is 5s; bumped to 120 to survive CPU inference.
  - Underlying cause of the slow CPU run: NVIDIA driver broken (kernel `6.17.0-29` missing matching `linux-modules-nvidia-595-open` package). Diagnosed and noted a fix to apply via sudo user.
- **First successful response**: 200 OK, qwen3:8b answered, ~5 tok/s on CPU. Goal now: parse with `response.json()` and extract just `message.content`.
- **Next**: clean response parsing, then handle qwen3's `<think>...</think>` blocks (or switch to `qwen3-nothink`).

---

### 2026-05-26 — Response parsing + first `chat()` wrapper

- GPU driver fix confirmed working (RTX 4060 visible, driver 595.71.05, CUDA 13.2). Ollama back on GPU.
- **Response parsing**: switched from `response.text` (raw JSON string) to `response.json()["message"]["content"]`. Detour through Python inspection tools (`type`, `dir`, `vars`, `pprint.pp`) to map the response shape interactively.
- **Tooling refresher**: covered `python -i`, `python -c`, `python -m pdb`, and `breakpoint()`. Notes added to `notes.md` as a cheatsheet — three sections: object inspection, REPL entry points, pdb commands.
- **First abstraction — `chat(messages: list[dict]) -> str`**:
  - Lifted `MODEL` and `OLLAMA_URL` to module-level constants.
  - Function builds payload, POSTs, returns just the assistant content.
  - Side effect: `import agent` no longer hits the network — sanity check via `python -c "import agent"` works.
- **First error-handling attempt (parked)**:
  - Wrapped in `try/except BaseException`, returned status code or exception text as a string on failure.
  - **Critique surfaced (not yet applied)**: function lies about return type — error strings and success strings are indistinguishable, will poison conversation history downstream. `BaseException` swallows `KeyboardInterrupt`.
  - **Recommended direction for next time**: drop the try/except, use `response.raise_for_status()`, let exceptions propagate. Design a real error model only when a caller actually needs one.
- **Next**: revisit error handling (Option A: let it raise), then move to multi-turn conversation (append assistant reply to `messages` and loop).
