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
