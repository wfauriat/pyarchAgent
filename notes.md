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

