# Sandboxing & curated primitives — design discussion

> Status: **discussion / parked** (2026-06-03). Not yet implemented. Pick-up notes
> for two related-but-distinct security threads. No code decisions are final here.

## Why now

`CLAUDE.md` says to add guardrails "when the agent starts executing real things."
It now does: `Agent.run` → `_execute` → `run_bash` shells out for real (subprocess,
`timeout=10`, `stdin=DEVNULL`). Current defenses: low-priv account + human y/n gate
(`_approve_y_n`) + git for recovery. Time to design the next layer.

**The one thing to get straight:** the two threads solve *different* problems and
are **not substitutes**.

- **Sandboxing** = blast-radius containment, at the **OS layer**.
- **Curated primitives** = legibility + least-privilege, at the **app layer**.

Defense in depth wants both.

---

## Thread 1 — Sandboxing (blast-radius containment)

OS-layer concern: given that `run_bash` executes, how much can it damage? Independent
of how nice the tool surface is.

### Start from the threat model, not the mechanism

Today's gate (human y/n + low-priv + git) handles well:
- **Accidental** destruction (wrong `rm`, too-broad `find -delete`).
- **Visibly** malicious commands a human rejects.

Handles poorly:
- **Prompt injection** — once tool *output* (file contents, web pages) re-enters the
  model, untrusted text can steer it. *This is the threat that actually forces a sandbox.*
- **Subtle commands** — humans approve fast and rubber-stamp; gate strength decays.
- **Unattended mode** — no human, no gate.

### The menu (cheap → strong)

1. Human gate only (today).
2. **Process limits** — `resource` rlimits (CPU, address space, nproc, file size) +
   existing `timeout`/`stdin=DEVNULL`. Pure-Python, no deps. Stops resource
   exhaustion; nothing else.
3. **Filesystem confinement** — restricted cwd, or namespaces.
4. **Container** — Docker/Podman, read-only rootfs, no network, tmpfs workdir.
5. **bubblewrap / gVisor / firejail** — unprivileged namespaces + seccomp. `bwrap` is
   the sweet spot for a low-priv account (no daemon, no root).
6. **Ephemeral remote VM** — strongest, most infra.

### Architectural point (the craft lesson)

Sandboxing is a property of the **executor**, not the loop or the backend. `run_bash`
is one function behind the registry, reached through `Agent._execute`. So the clean
move — mirroring the `approve` and `Backend` seams — is to make execution an
**injected dependency** (an `Executor` Protocol), default = today's local subprocess.
Then "local / rlimited / containerized" is a swap, not a rewrite.

> **Build the executor seam first.** Costs nothing in capability; unlocks everything
> above it.

### Two cautions

- **Don't build a command blocklist.** `probe_bash` already proved it's theater —
  qwen3 produced *different* commands for the same task run-to-run, and
  `find -delete` ≡ `find -exec rm`. You can't pattern-match shell safely. Confine the
  *environment*, not the *string*.
- **Sandbox to a profile, not in the abstract.** A no-network read-only sandbox can't
  edit your repo or run `pytest` — most of what a dev agent is *for*. The boundary must
  match the use case (e.g. "writable repo dir, no network" rather than "read-only
  everything").

---

## Thread 2 — Curated primitives (legibility + graded policy)

The idea: alongside (or instead of) one `run_bash(command)`, expose purpose-specific
tools — `read_file`, `write_file`, `edit_file`, `move`, `run_python`, `search`, …

### Framing correction up front

**Curated primitives are primarily a legibility + least-privilege play, NOT a
containment play.** As long as `run_bash` stays in the registry, adding primitives does
**not** reduce capability — a model (or an injection) just uses bash. What they *do* buy:

1. **Legibility — the killer argument.** Approving
   `run_bash("find . -name '*.py' -exec rm {} \;")` requires parsing shell.
   `delete_files(paths=[…])` or `read_file("x.py")` — the tool name *is* the intent.
   The `approve` gate gets far stronger when the call is self-describing.
2. **Graded policy / least privilege.** One `run_bash` collapses everything to one risk
   level. Primitives let you auto-allow `read`/`search`, confirm `write`/`edit`/`mv`, and
   gate `run_bash`/`run_python` as the escape hatch. This is the natural evolution of
   `_approve_y_n` → a policy table keyed on `tc.name` — and `approve(tc)` already
   receives the `ToolCall`, so it's a drop-in.
3. **Structured args are validatable.** `write_file(path, content)` can check `path` is
   under an allowed root *before* running. `run_bash("…")` can't be validated without
   parsing shell (the blocklist trap again). Structured intent is checkable; a command
   string isn't.
4. **Fewer model errors.** The probe showed qwen3 emitting varying, sometimes-wrong
   shell. Models call `read_file(path=x)` more reliably than they compose correct
   `find`/quoting.

### Pushbacks on the "build on bash, surface as primitives" framing

- **"Built on bash in core logic" — only for some.** For file ops, *don't* shell out —
  implement on Python stdlib (`pathlib.read_text`/`write_text`, `shutil.move`). Avoids
  shell-injection entirely, portable, and is the actual point of a purpose-specific tool.
  Reserve subprocess/bash for `search` (shelling to `rg`/`grep` is fine) and the `run_*`
  escape hatches.
- **`run_python` is not "safer" than `run_bash`.** Arbitrary Python is full code
  execution (`import os; os.system(...)`, sockets, …). A *different* arbitrary-code
  primitive, not a tamer one — same high-risk bucket, same gating.
- **More tools isn't free.** Every tool's schema rides in every prompt (you saw the
  token jump when tools are declared), and a big list makes the model pick wrong. The
  registry makes adding tools cheap — which is a *temptation*. A small, sharp set beats
  a sprawl.

### Builds on what already exists

- The **registry** is exactly the mechanism: each primitive is a
  `Tool(name, description, parameters, func)`; the per-vendor translators already render
  it. Thread 2 = "populate the registry with sharper Tools."
- The **`approve` seam** is where per-tool policy lives — it already gets the `ToolCall`.
- Connects to the deferred **`--auto`/`--dry-run`/`--confirm`** REPL policy selector
  (probe_bash's seed).

---

## Synthesis — three layers, defense in depth

- **Primitives** — least-privilege + legibility at the *app* layer.
- **Sandbox** — blast-radius containment at the *OS* layer.
- **Approval policy** — the decision layer tying them together; works far better with
  legible, structured tools.

Neither thread alone suffices:
- primitives without a sandbox → *legible but unbounded*;
- a sandbox around one opaque `run_bash` → *bounded but the human gate is blind*.

**Convergence on existing infrastructure — the per-context registry.** With the
executor seam + the registry + the policy gate, the tool set becomes a config choice:
- *attended* profile → full registry incl. `run_bash`, local executor, confirm-on-write;
- *untrusted/unattended* profile → only `read`/`search`, **no `run_bash`**, sandboxed
  executor.

That last profile is when curated primitives *finally* deliver containment — because the
dangerous tools simply aren't registered.

---

## Recommended sequencing (incremental, per project grain)

1. **Executor seam** (Thread 1 infra) — inject the executor, default local subprocess.
   Cheap; enables everything. Most "this project" move (another injected Protocol next to
   `Backend` and `approve`).
2. **Two read-only primitives** (`read_file`, `search`) — low-risk; immediately justify a
   smarter gate; validate the "primitive on Python stdlib, not bash" choice on safe ops.
3. **Policy gate** — `approve` → per-tool policy (auto-allow reads, confirm the rest);
   folds in the `--auto`/`--dry-run`/`--confirm` selector.
4. **Real sandbox** — rlimits → confined cwd → `bwrap`/container, when a trigger lands
   (unattended, or untrusted content reaching the model).

**Suggested first brick: the executor seam** — it's the Thread-1 piece that also makes
the Thread-2 escape hatch safe to keep.

---

## Open questions to resolve when picking this up

- **Executor seam shape**: `Executor` Protocol with what method? `run(command) ->
  BashResult`? Does it own the timeout/limits, or does `run_bash` still? (Leaning:
  executor owns *how* it runs; `run_bash`/tools own *what* to run.)
- **Primitive implementations**: confirm file ops on `pathlib`/`shutil` (no shell);
  `search` on `rg`/`grep` vs Python `os.walk`+`re`.
- **Path confinement**: is there an "allowed root" concept, and does it live in the
  primitive (`write_file` validates) or the executor (cwd jail), or both?
- **Policy representation**: a dict `{tool_name: Policy}` vs a callable; where do
  `auto`/`confirm`/`deny` live; how does the REPL select a profile.
- **Per-context registry**: how is a profile selected (CLI flag? constructor arg?), and
  does the backend get the registry injected (the long-deferred "inject tools into the
  backend constructor") so attended/unattended profiles differ without code changes.
- **Threat-model decision**: do we design for prompt injection now (changes everything —
  forces sandbox + no-`run_bash` profile for any untrusted input), or stay
  attended-only and treat the sandbox as resource/accident protection?
