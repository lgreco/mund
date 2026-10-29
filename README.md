# The Mundelein Problem

  *A collaboration between Leo, Claude, and two AY's worth of COMP 363 students!*

A simulation study of elevator demand from classrooms in Mundelein Center (Loyola University Chicago, Lakeshore Campus), limited to classes held before 4 PM.

The building has 54 classrooms on 12 floors and two elevator banks: four cars that reach floor 9 and two cars that reach floor 14. The study compares two behavioral measures (holding backpacks in front, and walking on floors 2 and 3) and a time offset for floors 10-14.

**The results are simulated, not measured.** Every timing parameter is an assumption, so treat the numbers as relative comparisons. The paper's limitations section describes the timing study needed to calibrate the model.

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

## Reproducing the results

Requires Python 3 with `numpy` and `matplotlib`, and a LaTeX installation for the paper.

```sh
cd model
python run_experiments.py        # optional argument: number of replicates (default 60)
cd ../paper
latexmk -pdf paper.tex
```

The runner is seeded, so the same replicate count regenerates the same tables and figures.

## Model parameters

Defaults and the experiment grid are in `Params` in `model/elevator_sim.py`: room occupancy, transfer share, adjacent-floor share, floor-group offset, walking and backpack compliance, car capacity, and travel, door, and boarding times.
