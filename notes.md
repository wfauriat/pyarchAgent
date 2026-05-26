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