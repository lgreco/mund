# The Mundelein Problem

  *A collaboration between Leo, Claude, and two AY's worth of COMP 363 students!*

A simulation study of elevator demand from classrooms in Mundelein Center (Loyola University Chicago, Lakeshore Campus), limited to classes held before 4 PM.

The building has 54 classrooms on 12 floors and two elevator banks: four cars that reach floor 9 and two cars that reach floor 14. The study compares two behavioral measures (holding backpacks in front, and walking on floors 2 and 3) and a time offset for floors 10-14.

**The results are simulated, not measured.** Every timing parameter is an estimate, and the simulator also embeds structural assumptions (for example, students never abandon a queue, and backpack compliance is a per-car coin flip) that no parameter sweep varies. Treat the numbers as relative comparisons from one model, not as predictions for the building. The paper lists the structural assumptions in a table and ranks the work needed to validate the model (see Future work below).

## Layout

| Path | Contents |
|---|---|
| `classrooms_per_floor.md` | Classroom count per floor |
| `scheduling_grid.md` | The registrar's standard scheduling grid (Fall and Spring) |
| `elevator_problem.md` | Problem statement, facts, and first-cut estimates |
| `model/elevator_sim.py` | Discrete-time simulator of one 15-minute class changeover |
| `model/run_experiments.py` | Experiment runner; writes tables and figures |
| `results/*.csv` | Result tables (60 replicates per scenario) |
| `paper/paper.tex`, `paper/paper.pdf` | Technical paper and its figures in `paper/figures/` |
| `tests/` | Verification tests for the simulator (`make test`) |
| `.claude/` | Project settings, hook, subagents, and skill for Claude Code (see below) |
| `.github/workflows/ci.yml` | CI: tests and a 2-replicate smoke run on every push |
| `Makefile`, `requirements.txt` | One-command build; pinned packages |
| `docs/STUDENT_GUIDE.md` | One-session lab for learning Claude Code with this project |

## Reproducing the results

Requires Python 3, `make`, and a LaTeX installation with `latexmk` for the paper.

```sh
make all              # venv, experiments (60 replicates), then paper
make results REPS=5   # quick smoke test; overwrites results/ and figures
make paper            # rebuild paper/paper.pdf only
make test             # simulator verification tests
```

Packages are pinned in `requirements.txt`; `make` creates `.venv` from it.

The runner is seeded, so the same replicate count regenerates the same tables and figures.

## Working with Claude Code

The repository is set up so Claude can check its own work. Everything lives in `.claude/` and is shared through git.

| Piece | File | What it does |
|---|---|---|
| Verifier | `make test`, `tests/` | Invariant tests (accounting, determinism, capacity, direction of effects). Claude can run them and read failures. |
| Hook | `.claude/hooks/post_edit.sh` | After any edit to `model/` or `tests/` Python, runs the tests; after any `paper/` LaTeX edit, rebuilds the paper. A failure goes back to Claude to fix. |
| Permissions | `.claude/settings.json` | Pre-approves `make test`, `make paper` and read-only git; asks before `make results`, `make all` and `git push`; denies force-push and `rm -rf`. |
| Subagents | `.claude/agents/` | `assumption-reviewer` (fresh-eyes audit of numbers and assumptions) and `citation-checker` (verifies references against real sources). |
| Skill | `.claude/skills/rerun-study/` | `/rerun-study`: test, regenerate results, rebuild the paper, and check that quoted numbers match the CSVs. |
| CI / headless | `.github/workflows/ci.yml` | Tests and a smoke run on every push. The same `make` targets also work headless, e.g. `claude -p "/rerun-study"`. |

Hooks and project settings need the folder to be trusted, and you may have to open `/hooks` or restart a session after
editing `.claude/settings.json`. The CI workflow and the subagents have not been run end to end yet.

## Model parameters

Defaults and the experiment grid are in `Params` in `model/elevator_sim.py`: room occupancy, transfer share, adjacent-floor share, floor-group offset, walking and backpack compliance, car capacity, and travel, door, and boarding times.

## Future work (ranked)

The next step is better evidence, not more model. In order of importance (details in the paper's Future work section; none is done unless noted):

1. **Validate against observation.** Record 5-10 changeovers (arrival intervals, boarding counts, car occupancy, queues, waits); calibrate on some and validate on the rest. Optionally, with building approval and within posted capacity limits, a small field test of car occupancy with and without a request to hold backpacks in front.
2. **Verify the simulator.** Automated tests (passenger accounting, capacity, movement, boarding, dispatch, termination) and small hand-computable scenarios. Fixed: the 3,600 s cutoff used to drop riders still waiting (up to 17 per replicate at full occupancy) from the wait and lateness statistics. The cutoff is now a 14,400 s backstop that no scenario reaches, unserved riders count as late, and results include an `unserved` column. Only the two full-occupancy rows changed, by under 0.2 points of lateness. A starter suite now exists in `tests/` (accounting, determinism, capacity, direction of effects); hand-computable scenarios and dispatch tests are still to be written.
3. **Systematic parameter sensitivity** aimed at break-even points: extra seats from backpacks (0-3), baseline capacity, occupancy, arrival concentration, boarding and door times.
4. **Structural uncertainty.** Two or three dispatch policies, alternative arrival and leaving behavior, students who leave the queue, per-rider compliance.
5. **Stronger statistics.** Confidence intervals on paired differences (scenarios already share seeds), plus journey time, P90/P95 delay, on-time rate, unserved counts, and results by floor and bank.
6. **Scheduling offsets over several consecutive periods**, or drop them. The current offset results are preliminary.
7. **Claims at the right evidence level.** Separate model results, robust findings, and empirical predictions. Partly done in the current draft.

Deferred to separate projects: a full-day simulator, optimization of room assignments, and detailed pedestrian modelling.
