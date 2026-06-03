# Python idiom audit — follow-up #2

*Date: 2026-06-03*
*Follows: `audit_python_idoms_2026-05-29.md` (package-wide) and `audit_python_idoms.md` (2026-05-27, `ollama_backend.py`)*

Re-assessment of Python concept coverage across `agentAPI/` (now ~680 LOC, 45 tests)
plus the root scripts (`probe_bash.py`, `scratch_subprocess.py`). Claims below are
grep-confirmed against the package and tests. The headline: the previous audits'
"missing" lists have **largely collapsed** — the tool-calling thread, the logging
thread, and the registry pulled in most of the deferred idioms at once.

---

## Closed since the 2026-05-29 audit

| Prior item | Status now | Evidence |
|---|---|---|
| **Logging** (craft-list gap, untouched in both prior audits) | **Closed** | `getLogger(__name__)` in all 3 backends; `basicConfig` + namespace floor at the app edge (`__main__.py`); lazy `%`-formatting; the library/application split. The 2026-05-27 verdict ("over-rotated on interface-design, under-rotated on observability") is now addressed. |
| **Iteration / comprehensions** (the #1/#2 "actual gap" in *both* prior audits — *"literally zero"*) | **Closed, pervasive** | `for` loops in all 3 backends + `agent.py` + `probe_bash.py`; list/dict/tuple comprehensions in `tools.py` (`REGISTRY = {t.name: t for t in _TOOLS}`, the `_to_*_tools` translators), tool-call parsing (`tuple([ToolCall(...) for tc in ...])`), and `probe_bash.py`. The single most-repeated criticism is resolved. |
| **`match` statement** (small-idiom gap) | **Closed** | `match`/`case` over the message union in all 3 `_to_*_messages` adapters, with `case _: assert_never(m)` for exhaustiveness. |
| **`Enum`** (small-idiom gap) | **Closed** | `StopReason(Enum)` in `backend.py` — neutral vocabulary (`END`/`TOOL`/`MAX_TOKENS`). |
| **`TypedDict` + `Literal`** (the 2026-05-29 **top pick**) | **Exercised → superseded** | Implemented as `Message = TypedDict{role: Literal[...], content}`, then **replaced** by a discriminated union of frozen dataclasses (`UserMessage \| AssistantMessage \| ToolResultMessage`). The idiom was learned and then the design outgrew it — see note below. |

---

## New idioms exercised (the prior audits couldn't list these)

- **`subprocess`** — the dormant **bash-fluency craft finally woke**. `run_bash` uses
  `subprocess.run(["bash","-c",cmd], capture_output=True, text=True, timeout=10,
  stdin=DEVNULL, check=False)`; `TimeoutExpired` handling; the bytes-vs-str gotcha
  (`_normalize` + `bytes(x).decode(errors="replace")`). A whole new stdlib area.
- **`match`/`case` + `assert_never`** — exhaustive structural dispatch over a sum type;
  the marquee new control-flow idiom.
- **Discriminated union via union type alias** — `Message = A | B | C` of frozen
  dataclasses (PEP 604), with the variants carrying mutually-exclusive fields.
- **`cast`** — the boundary cast at the Anthropic SDK edge (`cast(list[MessageParam],
  …)` / `cast(list[ToolUnionParam], …)`) to cross the TypedDict-invariance wall honestly.
- **Dataclass depth** — `kw_only=True` (`ChatResult`), `tuple[ToolCall, ...]` variadic
  typing, `Callable[..., str]` field types, frozen dataclasses holding callables (`Tool`).
- **`lambda`** — registry `func`s, `deny_all`, the `approve` default.
- **`del` statement** — the protocol-required-but-unused-parameter idiom (`del url,
  timeout` / `del system`) to satisfy a structural signature without a lint hint.
- **`enumerate`** (`probe_bash.py`), **dict comprehension keyed by attribute**
  (registry, name single-sourced off `Tool.name`).
- **pydantic `model_validate`** — used in a test to build a real `TextBlock` while
  dodging a Pylance kwarg-resolution quirk.
- **Registry / adapter pattern** — one neutral declaration → per-vendor translators,
  mirroring the inbound `_to_*_messages` adapters (anti-corruption layer, both directions).
- **Type-checker-as-workflow, deepened** — editor (Pylance) vs CLI (pyright) divergence,
  `getDiagnostics` as the editor oracle, and the lesson that a misplaced dict key in a
  `list[dict[str, Any]]` is invisible to the checker (caught only by schema-diffing).

### Note: `TypedDict`/`Literal` — exercised then retired

Worth recording as a *learning arc*, not a regression: the 2026-05-29 audit's #1
recommendation (`Message` TypedDict + `Literal` role) was implemented exactly, then
**superseded** when tool round-trips needed mutually-exclusive per-role fields — a job a
flat TypedDict can't model but a discriminated union of dataclasses can. The idiom was
genuinely practiced; the design then chose a richer tool. Both `TypedDict` and `Literal`
now grep to **zero** in the package for this reason.

---

## Still missing (grep-confirmed zero)

| Item | Status | Note |
|---|---|---|
| **`async` / `await`** | **Zero** | The largest remaining *conceptual* gap. The loop is synchronous; production LLM code is async-first (concurrent tool calls, streaming, parallel backends). Not yet pulled by a feature. |
| **Authoring decorators** (`def deco(func)`, `@wraps`) | **Zero** | Decorators are *used* (`@dataclass`, `@pytest.mark.xfail`) but never *authored*. |
| **Authoring context managers** (`__enter__`/`__exit__`, `@contextmanager`) | **Zero** | Only *consumed* (`with httpx.Client()`). |
| **`pathlib` / file I/O** (`open`) | **Zero, now queued** | No disk reads/writes yet — but the `sandboxing_and_primitives.md` thread proposes `read_file`/`write_file`/`mv` on `pathlib`/`shutil`. About to be pulled. |
| **pytest depth** — `parametrize`, `fixture`, `monkeypatch`/`mock` | **Zero, now *pressured*** | Tests landed broad (45) but the 3 backend test files are ~80% structurally identical (happy / tool / error / translator). The duplication is the live pressure for `parametrize` + a shared fixture. |
| **`functools`** (`partial`, `lru_cache`, `wraps`) | **Zero** | Would arrive with decorator authoring or caching a rendered schema. |
| **Generators / `yield`** | **Zero** | Comprehensions yes; generator *functions* no. Would land with streaming. |
| **`re` (regex)** | **Zero** | Still only pulled by `<think>`-stripping or output parsing; `think=False` sidesteps it. |
| Small idioms: `set`-membership (`in {…}`), `:=` walrus, `__post_init__`, `dataclasses.replace`, `try/else` | **Zero** | The quit check is still `== … or ==` rather than `in {…}`. Low-leverage. |

---

## Prioritization

Lens (unchanged): weight by (a) on the craft list, (b) under active pressure now,
(c) double-duty with an in-flight thread.

### 1. pytest depth — `parametrize` + a shared fixture (top pick)

Testing is on the craft list and went **broad but not deep**. The three backend test
files now repeat the same four shapes (happy / tool-call / error-translation /
translator-envelope) with only data differences — exactly what `@pytest.mark.parametrize`
and a fixture exist for. Double-duty: a named pytest-depth gap **and** a live
DRY pressure that's growing with every backend. Highest-leverage, self-contained.

### 2. Authoring a context manager (and maybe a decorator) — pulled by the next thread

The `sandboxing_and_primitives.md` executor seam is *naturally* a context manager
(`with sandbox(): …` / a resource-limited subprocess scope), and a per-tool
policy/retry wrapper is *naturally* an authored decorator. Both close "use-but-never-
author" gaps and double-duty with the live security thread. Front-loadable the moment
that thread opens.

### 3. `pathlib` / file I/O — arrives with the read/write primitives

Queued by the primitives thread (`read_file`/`write_file`/`mv` on `pathlib`/`shutil`,
deliberately *not* shelling out). Low new-concept risk, immediate relevance.

### Defer until pulled

- **`async`** — biggest conceptual gap, but no feature pulls it yet; consistent with the
  prior audits' "defer until a feature lands." Would arrive with streaming or concurrent
  tool execution.
- **`re`, `functools`, generators, walrus, `__post_init__`, `dataclasses.replace`,
  `try/else`, set-membership** — defer; none are pressured.

---

## The actual gap

Two prior verdicts (testing, then the TypedDict double-duty) are both **resolved**. The
current standout is narrower and more mature: **testing has scaled in breadth but not in
technique.** 45 tests, all hand-rolled fakes (a deliberate and good early choice) — but
the three backend suites are now near-duplicates, and `parametrize`/`fixture` are both
the missing pytest idioms *and* the right tool to collapse that duplication. It's the one
gap that is simultaneously on the craft list, under active pressure, and self-contained.

The second axis worth naming is **authoring vs using**: every decorator and context
manager in the codebase is consumed, none authored — and the sandboxing thread is about
to hand over the most natural possible occasion to author both. That's the
front-loadable one.

**Recommendation:** when next touching tests, do one deliberate `parametrize` + fixture
pass over the backend suites; and treat the executor seam (when the sandboxing thread
opens) as the occasion to *author* a context manager rather than reach for one.
