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

---

### 2026-05-27 — VSCode environment setup (deliberate detour from code)

- Step back from agent code to set up a proper dev environment. Three pieces tackled in order: Claude Code IDE extension → autocomplete posture → debugging config.
- **Claude Code extension** installed via `code --install-extension anthropic.claude-code`. Inline diff UI, auto-context from selection/open tabs, `Ctrl+Esc` to invoke on selection.
- **Autocomplete philosophy**: distinguished three independent layers — AI ghost-text (off, never installed), IntelliSense popups (off by default), parameter hints (kept on). Reason: in acquisition mode, auto-popups become ratification, not learning. Manual `Ctrl+Space` summons IntelliSense when genuinely needed.
- **`.vscode/settings.json`** written with 6 keys: `editor.quickSuggestions` all off, `suggestOnTriggerCharacters: false`, `parameterHints.enabled: true`, `wordBasedSuggestions: off`, `python.analysis.autoImportCompletions: false`, `python.analysis.typeCheckingMode: basic`.
- **Scope decision**: settings placed at `agentBuilding/.vscode/`, not at the training repo root. Narrower than originally suggested — keeps the discipline local to this project; revisit later if it should be ambient across `tutorials/`/`kata/`.
- **Linux gotcha**: `Ctrl+Space` often captured by IBus/fcitx at the OS level. Verified the suggestion engine works via command palette → "Trigger Suggest" before debugging keybinding.
- **`.vscode/launch.json`** written with a single generic "Python: Current File" config: `type: debugpy`, `request: launch`, `program: "${file}"`, `console: integratedTerminal`. Skipped the agent.py-specific config — premature for now. Verified F5 hits a gutter breakpoint and pauses in `agent.py`.
- **IntelliSense cheatsheet** appended to `notes.md` (keybindings table + icon legend + Linux-capture warning).
- **Next**: back to agent code. Pending from previous session: revisit `chat()` error handling (let it raise via `response.raise_for_status()`), then multi-turn loop.

---

### 2026-05-27 — `chat()` error model: transport + protocol layers

- **Working mode**: deliberated up-front on whether to do "Claude writes broken code, user PR-reviews it" vs tutor-first. Settled on tutor-first now, PR-review exercise reserved for a later function (conversation history or tool dispatcher) so design-and-write reps come first.
- **Three-layer failure taxonomy** adopted as the mental model for the HTTP call: **transport** (couldn't reach server — `httpx.RequestError` family), **protocol** (non-2xx status code — `httpx.HTTPStatusError`), **contract** (response received but JSON shape wrong — `KeyError` / `JSONDecodeError`). Each layer has its own moment in the call sequence and its own remediation.
- **Design call**: transport = *runtime* concern, surface as catchable exception so caller can retry/alert. Protocol + contract = usually *programmer errors*, fail loud with good context. Don't catch what you can't sensibly handle.
- **Return-type honesty**: identified the old pattern (`except BaseException: return str(e)`) as a lying return type — caller can't distinguish a real reply from an error string. Replaced with raise-based error model. `-> str` now actually means "the assistant's reply, or this function raises."
- **Custom exceptions, not pass-through**: introduced `BackendConnectionError` and `BackendResponseError` as module-level classes. Chosen over (a) bare `raise` of httpx exceptions and (b) builtin `ConnectionError` — reason: project explicitly plans a second backend (Anthropic), and both adapters should raise the same application-level types so caller code stays backend-agnostic from day one. Common `BackendError` base class noted but deferred.
- **Concrete idioms picked up**: `response.raise_for_status()` to convert non-2xx to exception; `raise X(...) from e` to wrap while preserving the original via `__cause__`; implicit string concatenation inside parens for multi-line f-string messages (no `+`, no `\`).
- **httpx hierarchy insight**: `RequestError` and `HTTPStatusError` are *siblings* under `HTTPError`, not parent/child — so a single try block with two except clauses suffices, no nested try needed. Current code still has the nested form; flatten on next pass.
- **Empirical confirmations**: happy path returns model reply; bogus-port test produces `BackendConnectionError` with chained `httpx.ConnectError` underneath. Protocol path not yet exercised against a live Ollama (needs real port + nonexistent model name).
- **Side**: added `editor.rulers: [80]` to `.vscode/settings.json` for a soft 80-col guide. Brief detour on Python multi-line string idioms.
- **Next**: (1) flatten the nested try block; (2) fix the misleading `BackendResponseError` message to include `e.response.status_code` and `e.response.text`; (3) provoke and confirm the protocol path empirically; (4) decide whether to add a `BackendError` common base; (5) then move on to multi-turn conversation history.

---

### 2026-05-27 — Flattened try, refactor pass, contract layer explored & deferred

- **Flattened the nested try in `chat()`.** Two `except` clauses (HTTPStatusError, RequestError) now sit as peers on a single try — matches the transport/protocol mental model and matches httpx's sibling exception hierarchy. Indentation gotcha fixed on the way.
- **Small refactor pass (5 changes, all accepted):**
  - Dropped `from typing import List` → `list[dict]` (Python 3.9+ builtin generic).
  - Docstring grew a `Raises:` section so the return-type honesty extends to the doc.
  - `payload` dict reformatted with newline + trailing comma (key-stable diffs).
  - `REQUEST_TIMEOUT = 60` lifted to module-level constant alongside `MODEL` / `OLLAMA_URL`.
  - Indentation tidied.
- **Provoked the protocol path empirically.** Pointed `MODEL` at a nonexistent name; Ollama returned 404, `raise_for_status()` fired, `BackendResponseError` surfaced with status + body. Chained traceback via `from e` visible — confirms the design from previous session.
- **Explored a contract layer.** Added `BackendError` base + `BackendContractError` subclass + `except (KeyError, TypeError, json.JSONDecodeError)` tuple-catch, motivated by anticipated multi-backend symmetry. Provoked it with `{"foo": "bar"}["message"]`. First version had two bugs the test surfaced: `e.response` doesn't exist on these exception types (would itself raise `AttributeError` and mask the wrap), and missing `from e`. Both fixed; the chained traceback then read cleanly.
- **Decided to remove the contract layer for now.** Today it adds no information over the bare `KeyError` traceback (the wrapper just re-raises `str(e)`). When the Anthropic backend lands and contract shapes actually diverge, bring it back with a real message (e.g. include the actual keys received). `BackendError` base + the two real subclasses (connection/response) stayed — they have meaningfully different retry semantics.
- **End-state `agent.py`:** 37 lines. Three exception classes (base + two), two except clauses, two `from e` chains, happy path is a 4-line straight read. Verified working against live Ollama (qwen3:8b on GPU).
- **Idioms picked up along the way:** Python 3.11+ traceback underline (`~~~^^^` pointing at the failing subexpression), the distinction between *"direct cause of"* (from `raise X from Y`) vs *"during handling of"* (implicit, often a bug in the except block).
- **Next:** multi-turn conversation history — append assistant reply to `messages`, loop.

---

### 2026-05-27 — `chat()` design audit, parameterization pass, rename to `ollama_backend.py`

- **Design audit of `chat()` as a module-level API** (vs script-level function). Identified five things that would matter once the function gets a second caller or a second backend: (1) module-level constants read implicitly, (2) `httpx.post` creates+discards a client per call (no DI seam, no connection reuse), (3) `"think": False` hardcoded in the payload (Ollama- and qwen3-specific), (4) return type is bare `str` — soon insufficient for token counts / stop reasons / tool calls, (5) no abstraction over backend choice.
- **Applied (1)–(3) one step at a time** so each change was reviewable in isolation:
  - **Parameterize config** as keyword-only args with module-constant defaults: `model`, `url`, `timeout`. Use of the `*,` separator forces keyword calls at the override site — readable when there are 3+ optional args.
  - **Inject `httpx.Client`** via `client: httpx.Client | None = None`. Default `None` falls back to `httpx.post()` (today's behavior); passing a client enables connection reuse, shared headers (auth), and test-time injection of fakes. Avoided `client = httpx.Client()` as default — that's the mutable-default-at-import footgun.
  - **Expose `think`** as a keyword arg. Was hardcoded; now per-call.
  - Default-only call site (`chat(messages)`) is unchanged — `__main__` block needed no edits. Good shape for API evolution.
- **Parked (4) — structured return type.** Promoting to `@dataclass ChatResult { content, tokens_in, tokens_out, stop_reason, ... }` is the right move *when* a caller actually needs more than the assistant string. Doing it now is speculative. Note: widening this return type later is a breaking change for any caller using `chat(...)` directly — accept that future churn, or front-load when the first real need lands.
- **Parked (5) — backend abstraction (ABC / Protocol / class refactor).** Sibling per-backend files (`ollama_backend.py`, future `anthropic_backend.py`) sharing the `BackendError` hierarchy is the working pattern for now. An abstract `Backend` ABC or `Protocol` becomes worthwhile the moment there are two adapters *and* a caller that wants to swap between them generically. Until then, "caller picks the import" is cleaner than an inheritance tree built for one occupant.
- **Renamed `agent.py` → `ollama_backend.py`** via `git mv` (history preserved). Triggered by realizing the error messages legitimately say "Ollama" — the issue wasn't the messages, it was the file name pretending to be generic. Now message specificity is honest: it *is* the Ollama backend reporting that Ollama is unreachable.
- **Error-message-specificity principle (worth keeping):** exception *types* are the backend-agnostic abstraction; exception *messages* should be backend-specific diagnostics. Removing the backend name from messages would erase useful information from tracebacks once multiple backends coexist.
- **Doc trail:** `notes.md` still contains three `import agent` cheatsheet examples — idiom-level, not strictly wrong, but candidates for refresh to `import ollama_backend` next time they're touched.
- **Next:** multi-turn conversation history (new session). Caller-side: append assistant reply to `messages`, loop. Likely the first place a long-lived `httpx.Client` gets passed in for real.

---

### 2026-05-27 — Multi-turn loop in `main()`, system prompt

- **First REPL loop**: `main()` with local `messages: list[dict]`, `with httpx.Client() as client:` around a `while True`, `input("> ")` per turn. EOF (`Ctrl+D`) and `KeyboardInterrupt` (`Ctrl+C`) caught as a tuple and treated as clean exits; `/quit` and case-insensitive `quit` also break. Client now persists across turns — first real use of the injection seam added last session.
- **State-management design**: build `user_msg` first, call `chat(messages=[*messages, user_msg], client=client)`, *then* append both `user_msg` and assistant reply to `messages`. If `chat()` raises, `messages` is unchanged — no orphaned user turn in history. The `[*messages, user_msg]` idiom is shallow-copy-plus-append in one expression.
- **System prompt**: added `PROMPT_SYSTEM` as a module-level constant alongside `MODEL` / `OLLAMA_URL`; prepended as `{"role": "system", ...}` before the loop starts. Empirically confirmed qwen3:8b honours it (pirate-persona test).
- **Idioms picked up**: implicit string concatenation inside parens (`( "...a" " ...b" )`) replacing backslash line continuation — same trick already used in the `BackendResponseError` f-string.
- **Parked**: promoting the system prompt to a `chat(..., system: str | None = None)` keyword arg. Today `main()` is the only caller; lift it into `chat()` when a second caller wants one without managing the messages list itself.
- **Next**: pick one of — structured return type (`@dataclass ChatResult`), second backend (Anthropic SDK), or first tool-calling scaffolding.

---

### 2026-05-27 — `ChatResult` dataclass, notes.md cheatsheets

- **Picked the dataclass thread** for learning, even though no caller pulled hard on widening the return type yet. Acknowledged the tradeoff: today `main()` only uses `.content`, so this is a learning-first widening — accept the future churn if more callers land.
- **Introduced `@dataclass(frozen=True) ChatResult`** with three fields: `content: str`, `tokens_in: int`, `tokens_out: int`. Frozen because a result is a value (a past outcome), not a state. Lives in `ollama_backend.py` for now; deferred extracting to a shared `types.py` until the second backend actually shows divergent shapes.
- **`chat()` now returns `ChatResult`.** JSON pulled into a local `data` so the construction reads cleanly: `ChatResult(content=data["message"]["content"], tokens_in=data["prompt_eval_count"], tokens_out=data["eval_count"])`. `main()` migrated to `.content` at two sites (history append, print) and gained a per-turn `tokens_in / tokens_out` debug line.
- **Empirical confirmation against live Ollama** (two-turn smoke test via `python -c`): turn 1 `tokens_in=45 / tokens_out=17`, turn 2 `tokens_in=78 / tokens_out=4`. Input grew with accumulated history; output tracked reply length ("Arrr!" → 4 tokens). Numbers are real, not zeros.
- **Contract assumption widened.** The construction assumes `prompt_eval_count` and `eval_count` are always present in Ollama's response — same contract-layer concern explored and parked previously. Left as a loud-on-failure `KeyError` for now (better than silent zeros in development).
- **`notes.md` got two cheatsheets** at "more than notes, less than full docs" depth (deliberate choice — coverage over exhaustivity):
  - **Dataclasses + typing primer**: minimal form, the four decorator knobs (`frozen` / `slots` / `kw_only` / `order`) with when-to-use, the `field(default_factory=...)` mutable-default rule, helpers (`asdict` / `astuple` / `replace` / `fields`), an annotation primer (`int | None`, `list[int]`, forward refs), and an anti-section (NamedTuple, pydantic/attrs).
  - **JSON stdlib**: the four entry points with the `s = string` mnemonic, type-mapping table (incl. dict-keys-become-strings round-trip pitfall), `dumps` formatting kwargs (`indent` / `sort_keys` / `separators` / `ensure_ascii` / `default` / `cls`), common patterns (pretty-print, JSON Lines), shell pipelines (`python -c`, `python -m json.tool`), gotchas, and when to reach for `orjson` / `ijson` / `pydantic`.
- **Idioms picked up**: `dataclasses.asdict()` as the standard bridge from frozen dataclass → JSON-serialisable dict (worth knowing for future logging); `python -m json.tool` as the no-`jq` stdlib JSON prettifier.
- **Next**: second backend (Anthropic SDK) — this is the call site that will actually pull on the parameterised `chat()` and on a shared `ChatResult` shape. Likely surfaces (a) the backend-abstraction decision (ABC vs Protocol vs sibling files) and (b) the `BackendContractError` reintroduction with a real message once shapes diverge.

---

### 2026-05-27 — `src/` layout, Anthropic backend happy path

- **Restructured into `src/`**: `ollama_backend.py` moved under `src/`, joined by new `src/backend.py` (shared `ChatResult` + `BackendError` hierarchy extracted) and `src/anthropic_backend.py`. Both backends now import the shared types from `src.backend`. `__init__.py` added. `.gitignore` extended for `.env`.
- **Anthropic `chat()` happy path landed.** Signature mirrors Ollama's where it can: `chat(messages, *, model, system, max_tokens, client) -> ChatResult`. Differences from Ollama parked in the signature itself: `system` (top-level Anthropic field, not a message-list entry) and `max_tokens` (required by the API, no default on the SDK side).
- **Bug squashed: `system=None` rejected by API.** Passing `system=None` through to `client.messages.create(...)` produced `400 invalid_request_error: 'system: Input should be a valid array'`. Distinction surfaced: "argument omitted" vs "argument explicitly null" are different things to an API that distinguishes optional from nullable. Fix is the conditional-kwargs idiom — build a dict, only add `"system"` when non-None, splat with `**kwargs` at the call site.
- **Lazy client instantiation.** `client: anthropic.Anthropic | None = None` with `if client is None: client = anthropic.Anthropic()` inside the function — mirrors the Ollama backend's transient-client pattern, also satisfies the type narrowing for `client.messages.create(...)`. SDK reads `ANTHROPIC_API_KEY` from env automatically, so the explicit `api_key=` parameter at the call site got dropped.
- **`load_dotenv()` placement deliberated.** Currently lives inside the `__main__` block of `anthropic_backend.py` — works for the script, but library imports of `chat()` won't auto-load `.env`. Three positions considered: module top-level (import side effect — surprising), inside `main()` (library users get the gotcha), or zero `load_dotenv()` in the library at all (push env management to the application edge). Left at current position; revisit when a unified REPL entry point lands.
- **Response shape mismatch noted.** Anthropic's `response.content` is a list of content blocks (`response.content[0].text` for plain text), `response.usage.input_tokens` / `.output_tokens` for token counts. Indexing `[0]` and assuming text is the happy-path read; the failure modes here are exactly where `BackendContractError` would come back with a real message.
- **Control-flow tangle caught and unwound.** Intermediate version had `client.messages.create(**kwargs)` accidentally nested inside the `if client is None:` branch, and the `if system is not None:` block placed *after* the call. Reshuffled to: build kwargs → conditionally add `system` → conditionally instantiate `client` → call → wrap in `ChatResult`. Top-to-bottom read, each step independent.
- **Parked: backend abstraction.** Two `chat()` functions now exist with overlapping-but-not-identical kwargs (Ollama: `url`/`timeout`/`think`; Anthropic: `system`/`max_tokens`). Two axes flagged for next session: (1) function vs object (constructor for per-backend config, method for per-call inputs) and (2) once classes exist, ABC vs `typing.Protocol` vs nothing. Read on the table: class-per-backend probably the bigger win; whether to formalise the static type comes after.
- **Next**: pick up the abstraction discussion. Sketch `OllamaBackend` / `AnthropicBackend` classes and let the call site reveal whether a `Protocol` is needed.

---

### 2026-05-29 — Import convention settled, root Makefile

- **Import convention decided: package + relative imports + `-m`.** Both backends now use `from .backend import ...`; `src/` is a real package (`__init__.py` earns its place); run via `python -m src.<module>` from the project root. Key framing: import form, run command, and pytest discovery are one coupled decision, not three. Rejected `from src.backend import` (hardcodes the layout name "src" into the namespace) and the flat-scripts option (relies on `sys.path[0]` magic, would need a `conftest`/path hack once tests arrive). Cost accepted consciously: lose `python src/x.py`, must use `-m`.
- **Root `Makefile` landed.** Targets `ollama_backend` / `anthropic_backend` → `$(PYTHON) -m src.<module>`, plus a `help` target placed first so bare `make` prints the menu instead of launching a REPL. `PYTHON` pinned to the venv absolute path (`/opt/venvs/pyDS/bin/python`) so it works from any shell, not just an activated one. `.PHONY` declared; tabs (not spaces) in recipes; `@echo` to suppress make's per-line command echo (the "doubled output" symptom). Bugs caught along the way: comma in `.PHONY` list (must be space-separated) and a `src.ollama_anthropic` module-name typo.
- **`test` target deferred.** pytest isn't set up (thread 2); holding the target until there's something to run rather than shipping a no-op.
- **`notes.md`: Makefile cheatsheet added.** Rule anatomy, the tab/echo/subshell gotchas, `=` vs `:=`, automatic + special variables, invocation flags, the self-documenting `help` idiom, and a when-not-to-use-make note (all-phony = task runner, where `just`/`tox` may fit better).
- **Next**: thread 1 abstraction (`OllamaBackend` / `AnthropicBackend` classes), or thread 2 (first pytest pass). The Anthropic error-handling gap (`BackendContractError`, raw `response.content[0].text`) is still parked.
