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
