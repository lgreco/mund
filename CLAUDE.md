# CLAUDE.md

Context for Claude Code when working in this repository. It carries over the decisions and history from the session that created the project, which began in a different folder.

## Project

A simulation study of elevator demand from classrooms in Mundelein Center (Loyola University Chicago, Lakeshore Campus). Scope: classes held before 4 PM only. Output: a simulator, result tables, and a LaTeX technical paper (`paper/paper.tex`). See `README.md` for layout and how to rerun.

## Established facts (stated by the user, not derived)

- 54 classrooms on 12 floors: 1:2, 2:4, 3:5, 4:8, 5:10, 6:11, 7:5, 10:4, 11:1, 12:1, 13:1, 14:2. None on floors 8 and 9.
- Two elevator banks: 4 cars and 2 cars. Only the 2-car bank reaches above floor 9; it serves all floors.
- Car capacity 3,000 lb, but cars typically leave with 4-6 riders (space is the limit, not weight).
- Classrooms seat 30-35; enrollment is often 15-25.
- Floor 1 is an atrium lobby (stairs from 1 to 2 feel like two flights). Students leave the building via the lobby.
- Full cars still stop at every lower floor on the way down, because the load-bypass is weight-based.
- Registrar's standard grid: MWF 8:15-3:35 (seven 50-minute blocks), TR 8:30-3:45 (five 75-minute blocks); every passing period is 15 minutes. Evening blocks (4:15 on) are out of scope.

## Decisions and scope (do not re-litigate)

- Only two behavior changes are in scope: **holding backpacks in front** (about +2 riders per car) and **walking on floors 2 and 3** (down especially). A courtesy rule was explicitly rejected as impossible.
- Out of scope: load-bypass settings, down-peak modes, anything that changes the elevator controller.
- Time-multiplexing was explored as a floor-group offset (0/5/10 minutes for floors 10-14). Group boundary sits at the empty floors 8-9, so students moving between adjacent floors are never split across groups.
- Adjacent-floor transfer share (10-30%) is a model parameter. Stairs for one-floor trips is an extension, not a requested measure.

## Model and results, in brief

- `model/elevator_sim.py`: one 15-minute changeover, one-second steps, collective dispatch, no full-car bypass.
- Main experiments use `p_occ=0.4` (chosen so the baseline shows a long line without collapse), `q_next=0.6`, `adj_share=0.2`, walking compliance 0.8 down / 0.5 up to floor 2 / 0.2 up to floor 3.
- Headline (60 replicates): baseline mean wait 5.2 min and 23% late; backpacks -31% wait; walking -6%; both -35% wait and 11% late. A 10-minute upper-floor offset clears queues about 20% faster but raises lateness with both measures (11% to 14%). Floor 10 is the worst floor.
- **All timing parameters are assumptions; nothing is measured.** Quote relative effects, not absolute minutes.

## Conventions followed

- Code uses a single `return` per function (carried over from the user's other repo's convention).
- Result files are CSV in `results/`; figures are PDF in `paper/figures/`. Reruns are seeded and reproducible.
- Environment: Python 3 with `numpy` and `matplotlib`. The earlier virtualenv lived in a temporary scratchpad and no longer exists; recreate one (`python3 -m venv .venv`, which `.gitignore` already excludes).

## Open items

1. **Timing study** (round-trip time from floor 9, seconds per stop, riders per stop) to calibrate the model; a natural COMP 363 exercise.
2. **Verify references** in the paper (Barney and dos Santos 1985; Strakosch 1998 were cited from memory).
3. **Authorship:** Claude is listed as an author at the user's request; some venues disallow AI authorship, in which case move to acknowledgments. Students are referenced collectively in a footnote.
4. Vary the leaver departure spread (fixed at 120 s) and test sensitivity of the queue peak to it.
5. A room-by-block schedule would replace the uniform occupancy assumption and allow per-block results.
6. The user edited `README.md` after the session (added a title and a collaboration line). Keep those edits.

## Session history (condensed)

1. Cleaned a pasted room list and counted classrooms per floor (`classrooms_per_floor.md`).
2. Retrieved the registrar's scheduling grid (`scheduling_grid.md`); user confirmed the copy was correct and limited scope to classes before 4 PM.
3. Discussed the two-bank problem and the cost of empty stops by full cars; user narrowed scope to the two behavior changes (`elevator_problem.md`).
4. Discussed time-multiplexing floors and the adjacent-floor transfer constraint; user asked for a parameterized model.
5. Built the simulator and experiment runner, ran 60-replicate experiments, and drafted the paper with seven figures.
6. Updated the authorship footnote, moved the project out of the prompts repo into this standalone repo, created the public GitHub repo `lgreco/mund`, and added the README. The user will push later changes themselves.
