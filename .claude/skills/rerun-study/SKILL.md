---
name: rerun-study
description: Regenerate the Mundelein results and rebuild the paper, then check that the paper's numbers match results/*.csv. Use after any change to the model or its parameters.
---

1. Run `make test`. Stop and report if anything fails.
2. Run `make results` (60 replicates; pass REPS=n only for a smoke test, and say so if you do).
3. Run `make paper`.
4. Compare the headline numbers quoted in `paper/sections/abstract.tex` and `results.tex` with the new
   `results/*.csv`. List every number that changed, and update the text only for numbers that moved.
5. Run `git diff --stat` and summarize what changed. Do not commit.
