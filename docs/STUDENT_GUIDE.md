# Student Guide: From Chatbot to Agentic Project

A one-session lab (about 90 minutes) for COMP 363. You will use this repository, a real if slightly silly
simulation study, to practice working with Claude Code in the terminal instead of pasting code in and out of a web chat.

## Why the CLI beats the chat window

| In the web chatbot | In the CLI (Claude Code) |
|---|---|
| You paste files in and copy answers out | Claude reads and edits files in your repo directly |
| Context is whatever you pasted | Context is the repo plus `CLAUDE.md` plus memory |
| You run the code and report errors back | Claude runs the code, reads the error, and fixes it |
| Every session starts from scratch | Decisions persist in files (`CLAUDE.md`, git history) |
| One long conversation | Plans, subagents, and skills break work into steps |

The rule of thumb: if you are acting as a copy-paste relay between the chat and your editor, move to the CLI.

## How this project was built (the worked example)

Read `CLAUDE.md` first. It records the project's history, and each step below maps to a habit worth copying.

1. **Facts before code.** The user cleaned a room list and fixed the scheduling grid *before* modeling anything
   (`classrooms_per_floor.md`, `scheduling_grid.md`). Habit: write down established facts in files, and separate them from assumptions.
2. **Narrowing scope by conversation.** The problem statement (`elevator_problem.md`) was refined until only two
   behavior changes remained. Habit: say what is out of scope, then record it so it is not re-litigated.
3. **Model, then experiments, then paper.** `model/elevator_sim.py`, `model/run_experiments.py`, then `paper/`. Every
   run is seeded, so results reproduce. Habit: ask for reproducibility from the start.
4. **Honest limits.** Every timing parameter is an assumption. The paper separates *parameter estimates* from
   *simulator structure*. Habit: make Claude state what is measured and what is assumed.
5. **Iteration on the artifact.** Fonts and the abstract were changed with short follow-up requests, and Claude
   rebuilt the PDF each time to check. Habit: small requests, verified by a build.

## Setup (10 min)

```sh
git clone https://github.com/lgreco/mund && cd mund
make venv
claude
```

Check that `make results REPS=5` runs (5 replicates is enough for a smoke test). It overwrites `results/` and
`paper/figures/`, so run `git restore results paper/figures` afterward unless you mean to keep the output.

## Tutorial: the building blocks

Each piece below has a one-paragraph explanation, where it lives in this repo, and a "try it" you can do in two minutes.

### CLAUDE.md: standing instructions

A plain Markdown file at the repo root that Claude reads at the start of every session. Put in it what Claude cannot
infer from the code: decisions, rejected ideas, conventions, how to run things. It is the cheapest and most valuable
piece of setup. *In this repo:* `CLAUDE.md`. *Try it:* ask "what is out of scope for this project?" and see where the
answer comes from.

### Memory: what carries over between sessions

Claude Code can also keep short notes about you and your preferences in a memory folder outside the repo. Use
`CLAUDE.md` for facts about the *project* (shared through git) and memory for things about *you* (not shared).

### Plan mode: think before editing

Plan mode (cycle with Shift+Tab) lets Claude read and propose but not change files. You review the plan, push
back, and approve. Use it whenever a change touches several files or you are unsure of the approach.

### Permissions: what Claude may do without asking

Every tool call (running a command, editing a file) goes through a permission check. You can approve one call, or
write rules in `.claude/settings.json` under `permissions`: `allow` (no prompt), `ask` (always prompt), `deny`
(never). Rules match like `Bash(make test)` or `Bash(git status*)`. *In this repo:* safe commands are allowed, `make
results` and `git push` ask, force-push is denied. Rule of thumb: allow what is read-only or cheap to undo.

### Hooks: automation the harness guarantees

A **hook** is a command that Claude Code itself runs when an event happens, such as just after Claude edits a file
or just before it runs a shell command. Claude does not decide to run it, so it cannot be forgotten. That is the
difference from an instruction in `CLAUDE.md`, which Claude might follow or might not.

- **Events:** `PreToolUse` (can block a call), `PostToolUse`, `UserPromptSubmit`, `Stop`, `SessionStart`, and others.
- **Matcher:** which tool the hook applies to, for example `Write|Edit`.
- **Input and output:** the hook receives JSON on standard input (the tool name and arguments). Exit code 0 means
  fine. **Exit code 2 means block or report**: what the script prints to standard error is fed back to Claude, which
  then fixes the problem.
- *In this repo:* `.claude/hooks/post_edit.sh` runs `make test` after a Python edit and `make paper` after a LaTeX
  edit. *Try it:* break a test on purpose and watch Claude receive the failure without you saying a word.
- Hooks run with your permissions, so read a hook before you trust a repo that contains one.

### Subagents: a fresh pair of eyes

A **subagent** is a second Claude with its own context window, its own instructions, and a limited set of tools. The
main session hands it a task and receives only its final report. Two reasons to use one: it has not seen the code
being reviewed, so it does not share the author's blind spots; and its long searches do not clutter your main
conversation.

- Defined as a Markdown file with a short header (`name`, `description`, `tools`) in `.claude/agents/`; the body is its
  instructions. Claude picks it when the description fits the task, or you can ask for it by name.
- *In this repo:* `assumption-reviewer` (read-only audit of numbers and assumptions) and `citation-checker`
  (verifies references against sources). Both are given no edit tools on purpose.
- Rule of thumb: subagents for *independent checking* and *wide searching*, not for work that depends on everything
  said earlier in the conversation.

### Skills and slash commands: reusable workflows

A **skill** is a folder with a `SKILL.md` file: a name, a description, and step-by-step instructions. You invoke it
as `/name`, and Claude may also pick it up when your request matches its description. Think of it as a saved recipe
for a task you repeat.

- *In this repo:* `.claude/skills/rerun-study/SKILL.md`, invoked as `/rerun-study`. It runs the tests, regenerates the
  results, rebuilds the paper, and checks that the paper's numbers match the CSVs.
- *Try it:* run `/rerun-study`. Then open the `SKILL.md` and change one step.

### Headless mode and CI: Claude without a terminal

`claude -p "<prompt>"` runs one prompt non-interactively and prints the answer, so it can sit inside scripts or
automation. CI (here GitHub Actions) runs a fixed list of commands on every push. The workflow in this repo runs
`make test` and a short smoke run, with no Claude involved: the checks are the same ones Claude uses, so a green CI
means the rules Claude follows are the rules the repo enforces.

### Worktrees: parallel experiments

A git worktree is a second checkout of the same repository in another folder, on its own branch. `claude --worktree
<name>` starts a session in one. Use it to try two designs at once (for example two dispatch policies), then compare
or discard them without disturbing your main working copy.

### MCP and connectors (not used here)

MCP servers give Claude extra tools, such as a browser, a database, or your calendar. This project does not need
any. Know that they exist, and that each one widens what Claude can touch, so enable only what the task needs.

### How the pieces fit

| You want Claude to... | Use |
|---|---|
| Know a fact or rule every time | `CLAUDE.md` |
| Be told it is wrong when it is wrong | A test or build it can run (`make test`) |
| Always do X after Y, no exceptions | A hook |
| Review work without bias | A subagent |
| Repeat a multi-step task | A skill |
| Stop asking about safe commands | A permission rule |
| Run without you | Headless mode / CI |
| Try two ideas in parallel | Worktrees |

If you can only add one thing to a project, add a test Claude can run.

## Exercises

Do them in order. For each, write down your prompt and what you would change about it.

### 1. Orient (10 min): let Claude read the repo

Prompt: *"Read CLAUDE.md and the README, then explain the model in five sentences and list what is assumed vs. measured."*
Compare against the paper's limitations section. Notice you pasted nothing.

### 2. Write a CLAUDE.md (10 min)

Delete nothing; instead, in a scratch branch, ask Claude to run `/init` and compare its result to the real `CLAUDE.md`.
What did the real one record that code alone cannot show (decisions, rejected ideas, history)?

### 3. Plan before you edit (15 min)

Switch to plan mode (Shift+Tab to cycle modes) and ask: *"Plan a sensitivity sweep over extra seats gained from
holding backpacks (0 to 3)."* Read the plan, push back on one thing, and only then approve it.
Goal: see that planning is cheaper than undoing.

### 4. Write the missing tests (20 min)

A starter suite is in `tests/` (run `make test`). The README still lists hand-computable scenarios and dispatch
tests as missing. Ask Claude for one: for example, one car, one floor, three riders, where you can predict every wait
by hand. Then **read the test**: does it test the model or just restate the code? Break the simulator on purpose
and confirm a test fails.

### 5. Add a feature, keep the rules (15 min)

Add a dispatch-policy option to `Params` (the README's "structural uncertainty" item). Constraints from
`CLAUDE.md` apply: single `return` per function, seeded runs, and no controller changes in the main experiments.
Did Claude follow the conventions without being reminded? That is what `CLAUDE.md` is for.

### 6. Close the loop with the paper (10 min)

Rerun the experiments, then ask Claude to update the affected table in `paper/sections/results.tex` and rebuild
the PDF. Check the numbers in the text against `results/*.csv` yourself.

### 7. Let the harness check Claude (10 min)

Open `.claude/settings.json` and `.claude/hooks/post_edit.sh`. Ask Claude to make a deliberately wrong edit to a
test, and watch the hook run the suite and send the failure back. Then run `/rerun-study` with `REPS=5` in mind (it asks
before running `make results`) and the `assumption-reviewer` subagent on the paper. Compare what the fresh-context
reviewer finds with what you found yourself.

## The agentic toolbox in this repo

| Idea | Where it is here | Why it matters |
|---|---|---|
| A verifier Claude can run | `make test` | Claude iterates until the check passes instead of asking you |
| Hooks | `.claude/hooks/post_edit.sh` | The harness runs them, so they cannot be forgotten or skipped |
| Subagents | `.claude/agents/` | A fresh context reviews without the author's blind spots |
| Skills / slash commands | `.claude/skills/rerun-study/` | A repeated workflow becomes one command |
| Permissions | `.claude/settings.json` | Fewer prompts for safe commands, a guardrail on risky ones |
| Headless and CI | `.github/workflows/ci.yml`, `claude -p` | The same checks run without you in the loop |
| Parallel worktrees | `claude --worktree <name>` | Try alternative dispatch policies side by side, then compare |

Commit `.claude/` to git: it is the part of the project that tells the next person (or the next session) how to work safely.

## Habits to take with you

- **Verify, don't trust.** Ask Claude to run the build or the tests, and read the output.
- **Put decisions in files.** Anything you would hate to re-explain belongs in `CLAUDE.md`.
- **Small, reviewable steps.** Commit between exercises (`git diff` is your review tool).
- **Know the permission prompts.** Read a command before approving it.
- **Cite carefully.** Claude cited two references from memory in this paper; they are flagged as unverified.
  Never submit a citation you have not looked up.
- **Disclose AI use.** This paper lists Claude as an author at the instructor's request; many venues and courses
  require acknowledgment instead. Follow your course's policy.

## Deliverable

A short write-up (one page) with: your best and worst prompt, one thing Claude got wrong that you caught, and
the diff of your feature from exercise 5.
