## Git cheatsheet

### Inspect (read-only, run these constantly)
``` bash
git status                          # what's changed, what's staged, what branch
git log --oneline --graph --all     # visual history of every branch
git log --oneline -10               # last 10 commits, terse
git diff                            # unstaged changes (working tree vs index)
git diff --staged                   # staged changes (index vs HEAD)
git show <commit>                   # diff + message of a specific commit
git blame <file>                    # who last touched each line
```

### Stage and commit
``` bash
git add <file>                      # stage a file
git add -p                          # stage *parts* of a file interactively — learn this
git restore --staged <file>         # unstage (keeps changes in working tree)
git restore <file>                  # discard unstaged changes (destructive)
git commit -m "msg"                 # commit staged changes
git commit --amend                  # edit last commit (only if not yet pushed)
```

### Branches
``` bash
git branch                          # list local branches
git switch <branch>                 # change branch (modern; preferred over checkout)
git switch -c <new-branch>          # create + switch in one step
git switch -                        # toggle back to previous branch
git branch -d <branch>              # delete merged branch
git branch -D <branch>              # force-delete (lose unmerged work) — careful
```

### Sync with remote
``` bash
git fetch                           # pull refs from remote, don't merge
git pull --rebase                   # fetch + rebase your local commits on top
git push                            # push current branch
git push -u origin <branch>         # first push of a new branch (sets upstream)
```

### Undo / fix
``` bash
git revert <commit>                 # safe undo: creates a new commit that reverses it
git reset --soft HEAD~1             # undo last commit, keep changes staged
git reset --mixed HEAD~1            # undo last commit, keep changes unstaged (default)
git reset --hard HEAD~1             # undo last commit + discard changes (DESTRUCTIVE)
git reflog                          # log of every HEAD move — lifesaver after a bad reset
```

### Rewriting history (local only — never on shared branches)
``` bash
git rebase <base>                   # replay your commits on top of <base>
git rebase -i <base>                # interactive: squash/reorder/edit commits
git cherry-pick <commit>            # copy a single commit onto current branch
```

### Stash (temporary shelf)
``` bash
git stash                           # shelve uncommitted changes
git stash pop                       # reapply + remove from stash
git stash list                      # see what's stashed
```

---

## Inspecting unknown objects in Python — cheatsheet

### Identity & shape

| Call | What it tells you |
| --- | --- |
| `type(x)` | The class, e.g. `<class 'dict'>` |
| `x.__class__.__name__` | Just the class name as a string (good for logs) |
| `len(x)` | Size — works on str, list, dict, tuple, set |
| `isinstance(x, dict)` | Boolean check against a type |

### What can I do with it?

| Call | What it tells you |
| --- | --- |
| `dir(x)` | Every attribute and method (noisy — filter dunders) |
| `help(x)` | Interactive docs / docstring |
| `vars(x)` or `x.__dict__` | Instance attributes as a dict (not on built-ins like `dict`) |
| `callable(x)` | Is it a function/method? |

Filter the noise from `dir`:

```python
[a for a in dir(x) if not a.startswith('_')]
```

### Dicts / JSON-like things

| Call | What it tells you |
| --- | --- |
| `x.keys()` | Top-level keys |
| `x.values()` / `x.items()` | Values / key-value pairs |
| `pprint.pp(x)` | Pretty-printed nested structure |
| `json.dumps(x, indent=2)` | Same idea, JSON-formatted string |


## Ways to get a live REPL on your script

| Command | Effect |
| --- | --- |
| `python -i agent.py` | Run script, then drop into REPL with all vars live |
| `python -c "import agent; ..."` | Import the script as a module and run inline code |
| `python -m pdb agent.py` | Step through from the very first line under `pdb` |
| `breakpoint()` in code | Pause execution and open `pdb` at that line |

#### `python -i` — run then REPL

- Runs the script normally, then drops to `>>>` with all globals still in scope.
- Survives exceptions: if the script raises, you land at the REPL with state intact (post-mortem).
- Exit with `Ctrl-D` or `exit()`.

#### `python -c` — one-liner runner

Executes the argument string as a script. Shell-friendly way to run Python without writing a file.

**When it's useful**
- One-off computations from the shell (math, format conversion, decoding).
- Probing a module: `python -c "import httpx; print(httpx.__version__)"`.
- Scripting / CI glue — a tiny bit of Python in a bash pipeline.
- Sanity checks: `python -c "import agent"` confirms the script imports cleanly.

**How it differs from the cousins**

| Form | Code lives... | Then... |
| --- | --- | --- |
| `python script.py` | in a file | runs and exits |
| `python -c "..."` | in the argument string | runs and exits |
| `python -i script.py` | in a file | runs, then drops to REPL |
| `python` (no args) | nowhere yet | opens REPL immediately |

**Examples**

```bash
# Version check
python -c "import sys; print(sys.version)"

# Parse one JSON field from a curl response
curl -s http://localhost:11434/api/chat -d @body.json \
  | python -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

# Test that a script imports without errors
python -c "import agent"
```

**Gotchas**
- **Quoting**: the code is a shell string, so `'` and `"` collide with shell quoting. Mix outer/inner quotes, or use `$'...'`.
- **No clean multi-line**: chain with `;`, but `if`/`for`/`def` blocks are painful — switch to a file or `-i` past that point.
- **No `__file__`**: there's no script path; `__name__` is `"__main__"` but `__file__` is undefined.

Rule of thumb: if it fits on one line and doesn't need indentation, `-c` is great. Past that, write a file.

---

## pdb cheatsheet

Python's built-in interactive debugger. Pause execution, inspect state, step through line by line.

### Entering pdb

| Method | When |
| --- | --- |
| `breakpoint()` in code | Pause at a specific line (Python 3.7+, no import needed) |
| `python -m pdb script.py` | Step from the very first line |
| `python -m pdb -c continue script.py` | Run normally, drop into pdb on exception (post-mortem) |

### Core commands

| Cmd | Long form | What it does |
| --- | --- | --- |
| `n` | `next` | Run the next line (step *over* function calls) |
| `s` | `step` | Step *into* the next function call |
| `c` | `continue` | Resume until next breakpoint or end |
| `r` | `return` | Run until the current function returns |
| `l` | `list` | Show source around the current line |
| `ll` | `longlist` | Show the whole current function |
| `p <expr>` | `print` | Evaluate and print an expression |
| `pp <expr>` | `pp` | Pretty-print (great for dicts) |
| `w` | `where` | Show the call stack |
| `u` / `d` | `up` / `down` | Move up/down the call stack |
| `b <line>` | `break` | Set a breakpoint |
| `q` | `quit` | Bail out |
| `h` | `help` | List commands; `h <cmd>` for details |

### Gotchas

- At `(Pdb)`, commands take priority over variable names. To inspect a variable named `n` or `c`, use `p n` or prefix with `!` (e.g. `!n = 5`) to force "treat as Python."
- You can run *any* Python at the prompt — assignments, method calls, imports. Current frame's locals/globals are all live.
- `Enter` on an empty line repeats the last command (handy when stepping with `n`).

---

## IntelliSense in VSCode

Suggestions are off by default (see `.vscode/settings.json`). Summon them manually.

### Keybindings

| Key | What it does |
| --- | --- |
| `Ctrl+Space` | Trigger suggestion popup (methods, vars, classes in scope) |
| `Ctrl+Shift+Space` | Trigger parameter hints (function signature) |
| `Esc` | Dismiss popup without accepting |
| `Tab` / `Enter` | Accept highlighted suggestion |

> On Linux, `Ctrl+Space` is often grabbed by IBus/fcitx for input-method switching. If it doesn't fire, unbind at the OS level or rebind `editor.action.triggerSuggest` in VSCode.

### Suggestion icons

| Icon | Meaning |
| --- | --- |
| ƒ (purple) | function / method |
| ◇ (blue) | variable |
| ▣ (orange) | class |
| ⬡ (green) | module |
| 🔑 (yellow) | keyword |

---

## Dataclasses — typed bags of fields

`@dataclass` reads your annotations and generates `__init__`, `__repr__`, and `__eq__`. Use when a class is mostly "named, typed fields" with little behaviour.

### Minimal form

```python
from dataclasses import dataclass

@dataclass
class ChatResult:
    content: str
    tokens_in: int
    tokens_out: int

r = ChatResult(content="hi", tokens_in=12, tokens_out=4)
r.content        # "hi"
print(r)         # ChatResult(content='hi', tokens_in=12, tokens_out=4)
```

### Decorator knobs

| Arg | Effect | When to use |
| --- | --- | --- |
| `frozen=True` | Instances are immutable; assignment raises `FrozenInstanceError` | Result / value objects (a past outcome, not a state) |
| `slots=True` (3.10+) | Adds `__slots__`; blocks new attrs, slightly lower memory | When discipline matters or you have many instances |
| `kw_only=True` (3.10+) | Forces keyword construction at every call site | Many fields, readability over brevity |
| `order=True` | Generates `<`, `<=`, `>`, `>=` from field tuple order | Sortable value objects |

### Defaults and mutable fields

Scalars: `x: int = 0` — fine.

Mutable defaults (`list`, `dict`, `set`) — same footgun as function args. `items: list = []` is rejected at class definition. Use `field(default_factory=...)`:

```python
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)
```

### Useful helpers

| Call | Effect |
| --- | --- |
| `dataclasses.asdict(obj)` | Recursive dict of fields — handy for JSON / logging |
| `dataclasses.astuple(obj)` | Same but as a tuple |
| `dataclasses.replace(obj, field=new)` | Returns a copy with one field changed (essential for `frozen=True`) |
| `dataclasses.fields(obj)` | Iterable of `Field` metadata objects — for reflection |

### Type annotations — the bit dataclasses lean on

`name: type` is the syntax dataclasses scan. At runtime Python doesn't enforce these — they're hints, picked up by type checkers (pyright, mypy) and by `@dataclass` to decide which class attributes are fields.

| Form | Meaning |
| --- | --- |
| `x: int` | x is an int |
| `x: int \| None` | int or None (3.10+ union syntax; pre-3.10: `Optional[int]`) |
| `x: list[int]` | list of ints (3.9+ builtin generic; pre-3.9: `List[int]`) |
| `x: dict[str, int]` | dict mapping str → int |
| `x: tuple[int, ...]` | tuple of any length, all ints |
| `x: "ChatResult"` | forward reference (string) — for self-referential types |

### When NOT to use a dataclass

- Class has substantial behaviour, not just fields → regular class.
- Just need a quick named tuple of values → `tuple` or `collections.namedtuple` / `typing.NamedTuple` (immutable, less ceremony, but no defaults below the first defaulted field).
- Need runtime validation on assignment → `pydantic.BaseModel` or `attrs` with validators. Dataclasses don't validate; annotations are hints only.

---

## JSON in Python — `json` stdlib

Four entry points, all in the `json` module. The naming is consistent: `load`/`dump` work on **f**ile-like objects; the `s`-suffixed `loads`/`dumps` work on **s**trings.

### The four functions

| Call | In | Out |
| --- | --- | --- |
| `json.loads(s)` | str (or bytes, 3.6+) | Python object |
| `json.dumps(obj)` | Python object | str |
| `json.load(fp)` | file-like (has `.read()`) | Python object |
| `json.dump(obj, fp)` | Python object + file-like | None (writes to `fp`) |

Mnemonic: **s = string**. No `s` = stream.

### Type mapping (JSON ↔ Python)

| JSON | Python |
| --- | --- |
| `object` | `dict` (keys always become `str` on parse) |
| `array` | `list` |
| `string` | `str` |
| `number` (integer) | `int` |
| `number` (float) | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Round-trip note: `tuple` → `list` (not back to tuple). `set` and `bytes` raise `TypeError` unless you provide a `default=` callback.

### Reading

```python
import json

# from a string (or response.text)
obj = json.loads('{"a": 1, "b": [2, 3]}')

# from a file
with open("data.json") as f:
    obj = json.load(f)

# from an httpx response (does loads on response.text under the hood)
obj = response.json()
```

Parse failures raise `json.JSONDecodeError` (subclass of `ValueError`). The exception carries `.msg`, `.doc`, `.pos`, `.lineno`, `.colno` — useful when reporting bad input.

### Writing

```python
# compact (default) — no whitespace
json.dumps({"a": 1, "b": [2, 3]})
# '{"a": 1, "b": [2, 3]}'

# pretty-print — almost always what you want for humans
json.dumps(obj, indent=2)

# to a file
with open("out.json", "w") as f:
    json.dump(obj, f, indent=2)
```

### `dumps` formatting kwargs

| Kwarg | Effect |
| --- | --- |
| `indent=2` | Pretty-print with that many spaces per level. Adds newlines too. |
| `sort_keys=True` | Stable key order — essential for diffable JSON / golden files |
| `separators=(",", ":")` | Override item/key separators. `(",", ":")` = most compact form (no spaces) |
| `ensure_ascii=False` | Keep non-ASCII chars literal instead of `\uXXXX` escapes |
| `default=fn` | Callback for objects the encoder doesn't know (e.g. `datetime`, custom classes) |
| `cls=MyEncoder` | Plug in a full `JSONEncoder` subclass for repeated custom logic |

### Common patterns

```python
# Pretty-print to stdout
print(json.dumps(obj, indent=2))

# Stable, diff-friendly serialisation
json.dumps(obj, indent=2, sort_keys=True)

# JSON Lines (one object per line — common log format)
with open("log.jsonl", "w") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

# Read JSON Lines back
with open("log.jsonl") as f:
    records = [json.loads(line) for line in f]
```

### Shell pipelines

`-c` form for ad-hoc inspection (from the earlier REPL cheatsheet):

```bash
# Extract one field from a curl response
curl -s http://localhost:11434/api/chat -d @body.json \
  | python -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

# Pretty-print any JSON on stdin
python -m json.tool < data.json

# Compact a JSON file in place (overwrite via temp)
python -c "import json,sys; print(json.dumps(json.load(sys.stdin)))" < big.json > small.json
```

`python -m json.tool` is the built-in CLI prettifier — handy when you don't have `jq` installed.

### Gotchas

- **Dict keys become strings.** `json.dumps({1: "a"})` produces `'{"1": "a"}'`. Parsing it back yields `{"1": "a"}` — the `1` is gone.
- **Floats and NaN.** `float("nan")` / `inf` are *not* valid JSON but `json.dumps` emits them by default. Pass `allow_nan=False` to raise instead — strict consumers will reject the default output.
- **No comments, no trailing commas.** JSON syntax is strict. If a file has comments it's "JSON5" or "JSONC", and `json.loads` will reject it.
- **`response.json()` vs `response.text`.** The former parses; the latter is the raw string. Calling `.json()` on a non-JSON body raises `JSONDecodeError`.
- **Custom types.** For `datetime`, `Decimal`, dataclasses, etc., either pre-convert (`dataclasses.asdict(obj)`) or pass `default=` to handle them on the fly.

### When NOT to use `json`

- Tabular data (rows × cols) → `csv` or `pandas`.
- Need schema validation, defaults, coercion → `pydantic` or `jsonschema`.
- Hot path with massive payloads → `orjson` / `ujson` (drop-in faster encoders/decoders).
- Streaming very large JSON files → `ijson` (iterative parser, doesn't load whole doc).

---

## Makefiles — build tool used as a task runner

`make` runs *recipes* to build *targets*, and rebuilds a target only when its *prerequisites* are newer (file timestamps). That incremental-build machinery is the real point. For us it's mostly a **task runner** — phony targets like `make chat_ollama` — which uses a fraction of make but is the most common day-to-day use.

### Anatomy of a rule

```makefile
target: prerequisites     # what to build, and what it depends on
<TAB>recipe               # shell commands — line MUST start with a literal tab
```

- make builds `prerequisites` first, then runs the recipe **only if** a prerequisite is newer than `target`.
- `target` and prerequisites are treated as **filenames** by default. Task-style targets (no real file) opt out via `.PHONY`.

### The three gotchas that bite everyone

- **Tabs, not spaces.** Recipe lines must begin with a literal TAB. Spaces give `*** missing separator. Stop.` (Check with `cat -A` — tabs show as `^I`.)
- **make echoes every recipe line before running it** → "doubled" output. Prefix the line with `@` to silence the echo (the fix for noisy `echo`/help targets).
- **Each recipe line runs in its own subshell.** A `cd foo` on one line does *not* carry to the next. Chain with `&&` + `\`, or set `.ONESHELL:`.

### Variables

| Form | Name | Behavior |
| --- | --- | --- |
| `=` | recursive | RHS re-expanded **every** time the var is used (lazy) |
| `:=` | simple | RHS expanded **once**, at definition |
| `?=` | conditional | assign only if not already set |
| `+=` | append | add to existing value |

Reference with `$(VAR)` or `${VAR}`. To pass a literal `$` to the shell, **double it**: `$$HOME`, `$$(date)` — a single `$` is make's, not the shell's.

### Automatic variables (inside a recipe)

| Var | Means |
| --- | --- |
| `$@` | the target name |
| `$<` | the first prerequisite |
| `$^` | all prerequisites (deduped) |
| `$?` | prerequisites newer than the target |
| `$*` | the stem matched by `%` in a pattern rule |

### Special targets

| Target | Effect |
| --- | --- |
| `.PHONY: a b` | `a`, `b` aren't files — always run them (list is **space**-separated) |
| `.DEFAULT_GOAL := help` | what bare `make` runs (otherwise: the **first** target in the file) |
| `.SILENT:` | suppress command echo globally (vs per-line `@`) |
| `.ONESHELL:` | run all of a recipe's lines in one shell (so `cd` persists) |

### Recipe line prefixes

| Prefix | Effect |
| --- | --- |
| `@` | don't echo this command |
| `-` | ignore its exit status (don't abort the build on failure) |
| `+` | run even under `make -n` |

### Invoking make

```bash
make                 # run the default goal (first target, or .DEFAULT_GOAL)
make target          # run a specific target
make -n target       # dry run: print recipes, don't execute (great for sanity checks)
make -s target       # silent: suppress echo for this run
make VAR=val target  # override a variable from the command line
make -C dir target   # chdir into dir first
make -j4             # run independent targets in parallel
```

### Self-documenting help (the idiom)

```makefile
.DEFAULT_GOAL := help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*## "}{printf "  %-18s %s\n", $$1, $$2}'
```

Tag each target with a `## description` comment, and bare `make` prints a clean menu. `$(MAKEFILE_LIST)` is the set of Makefiles read; `$$` escapes `$` so it reaches `awk`.

### Gotchas

- **Tabs** (yes, again — it's the single most common make error).
- **`$` is make's, `$$` is the shell's.** Forgetting the double-`$` in shell substitutions silently expands to an empty make variable.
- **`=` vs `:=`.** A recursive (`=`) var that references a later-defined var resolves lazily and "works"; the same with `:=` captures the (empty) value at definition. Surprises run both directions.
- **Forgotten `.PHONY`.** If a file named `test` exists and `test` isn't phony, `make test` prints "up to date" and does nothing.
- **Abort on first failure.** make stops at the first command that exits non-zero, unless the line is `-`-prefixed (or you pass `-i`).

### When NOT to reach for make

- make's real value is **timestamp-based incremental rebuilds** (compile/transform only what changed). If *every* target is phony (pure task runner), you're paying the tab / `$$` / one-shell-per-line tax for little of make's benefit.
- Pure task-running alternatives: `just` (justfile — no tab rule, saner variables), `tox`/`nox` (Python env + test matrix), `invoke` (tasks written in Python), npm scripts.
- **Cross-platform:** make assumes a Unix-ish shell; Windows needs care (or WSL/Git Bash).

---

## Packaging & imports — modules, packages, and the public API

How Python finds and *names* code, why relative imports break when you run a file directly, and how `__init__.py` lets you design a public API that's decoupled from your file layout.

### Modules, packages, and `sys.path`

- A **module** is a `.py` file. A **package** is a directory Python can import — either a *regular package* (has `__init__.py`) or a *namespace package* (no `__init__.py`, PEP 420).
- Import resolution walks `sys.path`. Its first entry depends on **how you launched Python** — which is the root cause of most "works here, breaks there" import pain:

| Launch | `sys.path[0]` is… | `__name__` | `__package__` | relative imports? |
| --- | --- | --- | --- | --- |
| `python pkg/mod.py` | `pkg/` (the script's own dir) | `"__main__"` | `""` | **break** |
| `python -m pkg.mod` | cwd (where `pkg` is visible) | `"__main__"` | `"pkg"` | **work** |
| `import pkg.mod` (elsewhere) | (already running) | `"pkg.mod"` | `"pkg"` | work |

The middle row is the one that lets `if __name__ == "__main__":` **and** relative imports coexist — which is exactly why the backends run as `python -m src.ollama_backend` rather than `python src/ollama_backend.py`.

### Absolute vs relative imports

| Style | Form | Resolved against |
| --- | --- | --- |
| absolute | `from src.backend import ChatResult` | `sys.path` roots |
| relative | `from .backend import ChatResult` | the current module's package (`__package__`) |
| relative (parent) | `from ..util import x` | one package up |

- Dots: `.` = this package, `..` = parent, `...` = grandparent.
- Relative imports require the module to *be inside a package* (non-empty `__package__`). Run a file directly and you get `ImportError: attempted relative import with no known parent package`.
- PEP 8 leans absolute for readability; relative is fine for intra-package wiring and is **rename-safe** (no hard-coded top-level name — rename the package and relative imports still resolve).

### `__init__.py` — the package's front door (the API-design lever)

Runs once on first import of the package. Its highest-value use: **re-export your public names** so callers import from the package, not from its internal file layout.

```python
# src/__init__.py
from .backend import ChatResult, BackendError

__all__ = ["ChatResult", "BackendError"]   # the explicit public surface
```

Now `from src import ChatResult` works, and you can move `ChatResult` between internal modules without breaking a single caller. This is the biggest "good API" move: the **public surface is decoupled from the file structure**. `__all__` also defines what `from src import *` exports and documents intent.

Keep `__init__.py` light — no heavy work or I/O at import time; every importer pays for it.

### `__main__.py` — make a package runnable

A `package/__main__.py` is what `python -m package` executes. Good home for a CLI entry point, so `python -m src` launches the app instead of you naming a specific submodule.

### Conventions that signal API boundaries

| Convention | Means |
| --- | --- |
| `_module.py` / `_name` | internal / private — not part of the public API |
| `__all__` in `__init__.py` | the explicit, supported public surface |
| no leading underscore | public — callers may depend on it |
| deep relative (`from ...a.b import x`) | smell: package too nested, or the boundary is wrong |

### The graduation step: an installable package

For code meant to be imported from elsewhere, declare it in `pyproject.toml` and `pip install -e .`. Then absolute imports resolve **regardless of cwd** — no `-m`-from-root dance, no `sys.path` hacks in tests. The proper "src layout" puts the importable package *under* `src/` (e.g. `src/agentbuilding/`) and installs it; bare `src` as the package name is an anti-pattern (you don't want `import src.backend` shipping the word "src" into the namespace). Out of scope while this is a single folder of scripts — it's where the project goes when it stops being one.

### Gotchas

- **Relative import in a directly-run file** → `attempted relative import with no known parent package`. Use `-m`, or switch that module to absolute imports.
- **Shadowing stdlib.** A local `json.py` / `queue.py` / `types.py` hides the stdlib module of that name — baffling import errors follow. Don't name modules after stdlib.
- **Circular imports.** A imports B which imports A → `ImportError` or a half-initialised module. Fixes: extract the shared piece into a third module, defer the import inside the function, or fix the dependency direction.
- **Naming the package `src`.** Leaks a layout word into every import. Fine for a private learning repo; rename before it's a real library.
- **Haunted imports after a rename** → stale `__pycache__`. Deleting the `__pycache__` dirs clears it.

---

## pytest — basics

A near-zero-config test runner: it **discovers** tests by name, runs them, and reports. You assert with the plain `assert` statement — pytest rewrites it under the hood so a failure shows the actual operands.

### Discovery & config

- Files `test_*.py` (or `*_test.py`); functions `test_*`; classes `Test*` (methods `test_*`, no `__init__`).
- pytest recurses from `testpaths`. Config lives in `pyproject.toml`:

```toml
[tool.pytest.ini_options]      # exact table name — a typo here is silently ignored
pythonpath = ["."]             # put project root on sys.path → `import yourpkg…` resolves
testpaths  = ["agentAPI/tests"]
```

pytest *warns and ignores* an unknown config key rather than erroring (`PytestConfigWarning: Unknown config option: …`) — so read the warnings.

### Anatomy — Arrange / Act / Assert

```python
def test_chat_parses_successful_response():
    client = FakeClient()                             # Arrange
    reply = chat(messages=[...], client=client)       # Act
    assert reply.content == "hi"                      # Assert
    assert reply.tokens_in == 12, f"got {reply.tokens_in!r}"   # optional message
```

- Plain `assert` is enough — pytest's introspection prints both sides (`assert 3 == 12`). No `assertEqual`/`assertTrue` ceremony.
- The optional `, "message"` adds context; pytest still shows the values.
- **Assert everything the unit derives from the input.** Under-asserting gives false confidence — a green test that would miss a swapped/dropped field.

### Test doubles via duck typing

- A **fake/stub** only needs the methods the code-under-test actually *calls* — it does **not** subclass the real type. `chat` calls `client.post(...)` then `.raise_for_status()`/`.json()`, so the fake implements exactly those. (Subclassing the real `httpx.Client` would construct a real connection pool — the dependency you're trying to avoid.)
- Inject the fake through a **seam** — here the `client=` parameter. That seam is *why* the code is testable without a network.
- Caveat for error paths: `except`/`isinstance` are **type**-based, not duck-typed. To exercise an `except SomeError`, the fake must raise the *real* exception type the code catches (see **Testing exceptions** below).

### Testing exceptions — `pytest.raises`

`pytest.raises(SomeError)` is a context manager that **inverts** the assertion: the block must raise `SomeError` (or a subclass). No raise — or a *different* type — fails the test.

```python
with pytest.raises(BackendConnectionError):
    chat(messages=..., client=failing_client)
```

Capture with `as excinfo` to assert on the exception itself — `excinfo.value` is the instance:

```python
with pytest.raises(BackendConnectionError) as excinfo:
    ...
assert "Could not reach" in str(excinfo.value)                   # the message
assert isinstance(excinfo.value.__cause__, httpx.RequestError)   # the `raise … from e` chain
```

| Access | What it is |
| --- | --- |
| `excinfo.value` | the raised exception instance |
| `excinfo.type` | its class |
| `excinfo.value.__cause__` | the original exception from `raise … from e` |
| `pytest.raises(Err, match=r"…")` | inline shorthand: assert the message matches a regex (`re.search`) |

- **Matching is by subclass, not exact type** — same nominal rule as `except`/`isinstance`. `pytest.raises(httpx.RequestError)` catches an `httpx.ConnectError` (a subclass). So test with a *concrete* error and assert against the base the code actually catches.
- **Error-translation pattern** (a unit wrapping a library's errors in its own): (1) the *fake* raises the real low-level error the code catches; (2) the *unit* catches it and re-raises its own; (3) the *test* asserts the unit's error — and asserting the **message** proves the unit read fields off the original (e.g. the status code), not merely that *something* raised.

### Running

| Cmd | Effect |
| --- | --- |
| `pytest` | discover + run (honors `testpaths`) |
| `pytest -v` / `-q` | verbose (one line/test) / quiet |
| `pytest -k EXPR` | only tests whose name matches EXPR |
| `pytest FILE::test_name` | run a single test |
| `pytest -x` | stop at the first failure |
| `pytest -s` | don't capture stdout (so `print`s show) |
| `pytest --collect-only` | list what *would* run, run nothing |

- **Exit code 5 = "no tests collected"** — non-zero, so it trips a `make test` / CI target even though nothing failed.

### Habits

- Name tests for **behavior**: `test_<unit>_<expected>`, not `test_fake_client`.
- One behavior per test; keep Arrange / Act / Assert visible.
- *To amend later:* `unittest.mock` / `monkeypatch`, fixtures, `@pytest.mark.parametrize`.

---

## Python classes — turning a function into an object

When a function accumulates config that's stable across calls plus a collaborator (an HTTP client, a connection pool), promoting it to a class lets the **constructor** hold that, leaving a **clean per-call method**. The big payoff: several implementations can then share one calling shape (interchangeable backends behind one interface).

### Anatomy

```python
class OllamaBackend:
    def __init__(self, *, model: str = "qwen3:8b",
                 client: httpx.Client | None = None) -> None:
        self._model = model                     # instance attribute (per-object state)
        self.client = client or httpx.Client()  # DI seam + lazy default

    def call_model(self, messages: list[dict], *,
                   system: str | None = None) -> ChatResult:
        ...                                      # reads self._model, self.client
```

- `__init__` runs at construction (`OllamaBackend()`) to **initialise** the already-created `self` — it's not what *makes* the object (that's `__new__`), it sets it up.
- `self` is the instance, passed automatically; it's the first parameter of every instance method.
- Instance attributes (`self.x = …`) are per-object state; assign them in `__init__`.

### The function→object decision — what goes where

| `__init__` (construction config) | the method (per-call input) |
| --- | --- |
| stable for the object's lifetime | varies every call |
| backend-specific (the stuff that *differs*) | must be **uniform** across implementations |
| collaborators / resources (HTTP client) | the actual request data (`messages`) |

The constructor *absorbs the differences*; the method signature becomes identical across implementations — which is what makes them swappable behind one interface.

### Dependency injection via the constructor

```python
self.client = client or httpx.Client()
```

- Pass a real client (or none → build a default); pass a **fake** in tests. When a collaborator becomes instance state, the test seam **moves from a method param to the constructor** (`OllamaBackend(client=FakeClient())`).
- `x or default()` is the lazy-default idiom. Don't put `client=httpx.Client()` in the signature — defaults evaluate once at *import*, the mutable-default footgun.

### Conventions

- `_name` = "internal, don't touch from outside" (convention, not enforced); public attributes have no underscore.
- Keyword-only args (`*,`) force callers to name config → readable construction with several optional args.
- Class names are `CapWords`; **module file names are `snake_case`** — class `OllamaBackend` lives in `ollama_backend.py`.

### Consumer vs implementation

A class should expose *one job*. The loop/orchestration that *uses* it (a REPL, a tool-calling loop) belongs to the **consumer**, not the class — keep it out of the backend module so the implementation stays swappable and the consumer depends only on the method shape.

### To grow later

- Formalising the shared method shape: `typing.Protocol` (structural) vs `abc.ABC` (nominal) — own entry, coming.
- `@property`, `@classmethod` / `@staticmethod`, dunders (`__repr__`; `__enter__`/`__exit__` for resource lifecycle, e.g. closing the client).
- `@dataclass` is the *value-object* end of the spectrum (see the Dataclasses entry); this entry is the *behavior + config* end.

---

## Abstraction — `Protocol` vs ABC (vs nothing)

An interface earns its keep **only when a consumer treats several implementations uniformly** (e.g. a REPL that holds "a backend" without caring which). Three ways to express "these share a shape":

| | nothing (duck typing) | **ABC** (`abc.ABC`) | **Protocol** (`typing.Protocol`) |
| --- | --- | --- | --- |
| Conformance | runtime — has the methods | **nominal** — must subclass | **structural** — matches the shape |
| Enforced | never (until it breaks at runtime) | at **instantiation** (missing `@abstractmethod` → `TypeError`) | **statically** (mypy/Pylance) |
| Shared code | n/a | yes (concrete methods on the base) | no — it's only a shape |
| `isinstance` | n/a | yes | only with `@runtime_checkable` (names, not signatures) |
| Dependency points | — | impl → abstraction (imports + subclasses) | consumer → shape; impls don't import it |

### ABC — nominal, can host shared code

```python
from abc import ABC, abstractmethod

class Backend(ABC):
    @abstractmethod
    def call_model(self, messages: list[dict]) -> ChatResult: ...

class OllamaBackend(Backend):            # must subclass
    def call_model(self, messages): ...
# OllamaBackend() with the method missing → TypeError at construction
```

### Protocol — structural, no inheritance

```python
from typing import Protocol

class Backend(Protocol):
    def call_model(self, messages: list[dict]) -> ChatResult: ...

def run(backend: Backend) -> None: ...   # anything with a matching call_model type-checks
# OllamaBackend does NOT subclass Backend — it just needs the right method
```

### Which to reach for

- **ABC** — you own all implementations *and* want shared concrete code on the base, or need runtime `isinstance`.
- **Protocol** — you're typing a *seam*, especially one you can't subclass (a third-party type like `httpx.Client`), or you want implementations **decoupled** from the interface (dependency inversion: the *consumer* declares the shape it needs; implementations conform without importing it).
- **nothing** — one implementation and no polymorphic consumer yet. Don't build an interface for a single occupant.

### Gotchas

- `Protocol` is **static-only** by default — `isinstance(x, MyProtocol)` raises unless the protocol is `@runtime_checkable`, and even then it checks only method *names*, not signatures.
- ABC **couples** implementations to the abstraction (they import and subclass it); Protocol points the dependency the other way — usually the cleaner seam.
- `...` (Ellipsis) is the conventional empty body for an abstract/protocol method.

---

## TypedDict — a static shape for dict-shaped data

When the value genuinely **is a dict** (a JSON/wire payload, kwargs, an API's expected input) but you still want the checker to know its keys and value types. `TypedDict` annotates that shape **statically** — at runtime the value is just a plain `dict`, zero cost, no instance.

### Minimal form

```python
from typing import TypedDict, Literal

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

m: Message = {"role": "user", "content": "hello"}   # checked: keys, literals, value types
```

A typo'd key (`"rol"`), a bad literal (`"system"`), or a wrong value type (`content=123`) is flagged where you write it. `dict` alone catches none of this — it has thrown the structure away.

### Knobs

| Form | Effect |
| --- | --- |
| `class M(TypedDict):` | all keys **required** (default, `total=True`) |
| `class M(TypedDict, total=False):` | all keys optional |
| `field: Required[T]` / `NotRequired[T]` | per-key override (3.11+, else `typing_extensions`) |
| `class M2(M):` | inherit + add keys (TypedDicts compose by subclassing) |
| `M = TypedDict("M", {"a-b": int})` | functional syntax — for keys that aren't valid identifiers |

### Construction — two checked forms

```python
{"role": "user", "content": "hi"}        # dict literal
Message(role="user", content="hi")        # call form — nicer errors, typo-safe
```

### Picking the tool (vs the neighbours)

| Use… | when… |
| --- | --- |
| `TypedDict` | the data is/stays a **dict**, built by your own trusted code (static check, no runtime cost) |
| `@dataclass` | you want an **owned object** with attribute access / behaviour (see *Dataclasses* entry) |
| `pydantic.BaseModel` | data crosses a **trust boundary** and needs **runtime validation** (raises on bad input) |

Mnemonic from this codebase: `ChatResult` is a **dataclass** (output you construct and read attributes off); a *message* is a **TypedDict** (a payload flowing straight into an HTTP body / SDK).

### Feeding a vendor's typed API (our `messages` case)

The reason this came up: the SDK wants `Iterable[MessageParam]`, and a bare `list[dict]` can't prove it matches.

- `Iterable` is **covariant**, so `list[Message]` → `Iterable[MessageParam]` *iff* `Message` is a subtype of the SDK's `MessageParam` (both are TypedDicts → compared **structurally**, key by key).
- If your `Message` lines up with the SDK's shape, no cast is needed. If it doesn't *quite* (TypedDict↔TypedDict subtyping is stricter than it looks — see gotchas), the honest escape hatch is a single `cast(...)` at the **one** vendor-boundary call — now casting from a shape you've actually typed, not from `dict`.
- Don't put the SDK's `MessageParam` in the shared `Backend` Protocol — that leaks one vendor into a neutral interface. Keep a vendor-neutral `Message` in `backend.py`; reconcile at the boundary.

### Gotchas

- **Static-only — no runtime validation.** A `TypedDict` annotation is a *promise*; nothing checks it at runtime. If the dict came from untrusted JSON, the annotation can be a lie — reach for Pydantic / a runtime check there.
- **No `isinstance`.** `isinstance(x, Message)` raises `TypeError` — there's no class to check against. (Same static-only nature as `Protocol`.)
- **Fields are mutable → invariant in subtyping.** Value types must match, not merely be assignable, when checking one TypedDict against another (the same mutable-attribute invariance that bit the client `Protocol`).
- **Access is `m["role"]`, not `m.role`** — it's a dict.

### When NOT to use

- Need runtime validation / coercion → `pydantic` or `attrs`.
- Want an object with methods, defaults below a defaulted field, attribute access → `@dataclass` / `NamedTuple`.

