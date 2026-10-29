"""Run the Mundelein elevator experiments and write tables and figures.

Usage: python run_experiments.py [replicates]
Outputs go to ../results (CSV) and ../paper/figures (PDF).
"""
import csv
import os
import sys
from dataclasses import replace
from multiprocessing import Pool

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from elevator_sim import Params, ROOMS, replicate, mean_of

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
FIGURES = os.path.join(HERE, "..", "paper", "figures")
BASE = Params(p_occ=0.4)
METRICS = ("mean_wait", "p90_wait", "late_frac", "empty_stop_frac", "clear_time", "riders",
           "se_mean_wait", "se_late_frac")

POLICIES = {
    "Baseline": {},
    "Backpacks": {"backpack": 1.0},
    "Walk (2,3)": {"walk_down": 0.8, "walk_up2": 0.5, "walk_up3": 0.2},
    "Both": {"backpack": 1.0, "walk_down": 0.8, "walk_up2": 0.5, "walk_up3": 0.2},
}


def std_err(results, key):
    vals = [r[key] for r in results]
    mu = sum(vals) / len(vals)
    var = sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)
    return (var / len(vals)) ** 0.5


def job(args):
    label, prm, n = args
    rs = replicate(prm, n)
    row = {"label": label}
    row.update({k: mean_of(rs, k) for k in METRICS if not k.startswith("se_")})
    row["se_mean_wait"] = std_err(rs, "mean_wait")
    row["se_late_frac"] = std_err(rs, "late_frac")
    row["queue_series"] = [r["queue_series"] for r in rs]
    row["wait_by_floor"] = {f: sum(r["wait_by_floor"][f] for r in rs) / len(rs) for f in ROOMS}
    return row


def write_csv(name, rows, extra_keys):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(list(extra_keys) + list(METRICS))
        for r in rows:
            writer.writerow([r[k] for k in extra_keys] + [round(r[m], 4) for m in METRICS])
    return path


def save(fig, name):
    os.makedirs(FIGURES, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, name))
    plt.close(fig)


def main(n):
    jobs, tags = [], []
    for pname, kw in POLICIES.items():
        for off in (0, 5, 10):
            jobs.append((f"{pname}|{off}", replace(BASE, offset_min=off, **kw), n))
            tags.append(("policy", pname, off))
    for share in (0.1, 0.2, 0.3):
        for pname in ("Baseline", "Both"):
            for off in (0, 5, 10):
                jobs.append((f"{pname}|{off}|{share}", replace(BASE, adj_share=share, offset_min=off,
                                                              **POLICIES[pname]), n))
                tags.append(("adj", pname, off, share))
    for occ in (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        for pname in POLICIES:
            jobs.append((f"{pname}|occ{occ}", replace(BASE, p_occ=occ, **POLICIES[pname]), n))
            tags.append(("occ", pname, occ))
    for bp in (0.0, 0.25, 0.5, 0.75, 1.0):
        jobs.append((f"bp{bp}", replace(BASE, backpack=bp), n))
        tags.append(("bp", bp))
    for wd in (0.0, 0.25, 0.5, 0.75, 1.0):
        jobs.append((f"wd{wd}", replace(BASE, walk_down=wd, walk_up2=wd * 0.6, walk_up3=wd * 0.25), n))
        tags.append(("wd", wd))
    for door in (5, 8, 12):
        for pname in ("Baseline", "Both"):
            jobs.append((f"{pname}|door{door}", replace(BASE, t_door=door, **POLICIES[pname]), n))
            tags.append(("door", pname, door))
    for q in (0.3, 0.6, 0.9):
        for pname in ("Baseline", "Both"):
            jobs.append((f"{pname}|q{q}", replace(BASE, q_next=q, **POLICIES[pname]), n))
            tags.append(("q", pname, q))
    for stairs in (0.0, 0.5, 0.8):
        for pname in ("Baseline", "Both"):
            for share in (0.1, 0.3):
                jobs.append((f"{pname}|stairs{stairs}|{share}",
                             replace(BASE, adj_stairs=stairs, adj_share=share, **POLICIES[pname]), n))
                tags.append(("ext", pname, stairs, share))
    with Pool() as pool:
        out = pool.map(job, jobs)
    table = list(zip(tags, out))

    def pick(kind):
        return [(t, r) for t, r in table if t[0] == kind]

    # Table 1: policy x offset (adj_share default)
    rows = []
    for t, r in pick("policy"):
        r2 = dict(r, policy=t[1], offset=t[2])
        rows.append(r2)
    write_csv("policy_by_offset.csv", rows, ("policy", "offset"))

    rows = [dict(r, policy=t[1], offset=t[2], adj=t[3]) for t, r in pick("adj")]
    write_csv("adjacent_share.csv", rows, ("policy", "offset", "adj"))
    rows = [dict(r, policy=t[1], occ=t[2]) for t, r in pick("occ")]
    write_csv("occupancy.csv", rows, ("policy", "occ"))
    rows = [dict(r, bp=t[1]) for t, r in pick("bp")]
    write_csv("backpack_compliance.csv", rows, ("bp",))
    rows = [dict(r, wd=t[1]) for t, r in pick("wd")]
    write_csv("walk_compliance.csv", rows, ("wd",))
    rows = [dict(r, policy=t[1], door=t[2]) for t, r in pick("door")]
    write_csv("dwell_sensitivity.csv", rows, ("policy", "door"))
    rows = [dict(r, policy=t[1], q=t[2]) for t, r in pick("q")]
    write_csv("transfer_sensitivity.csv", rows, ("policy", "q"))

    rows = [dict(r, policy=t[1], stairs=t[2], adj=t[3]) for t, r in pick("ext")]
    write_csv("adjacent_stairs_extension.csv", rows, ("policy", "stairs", "adj"))

    colors = {"Baseline": "#444444", "Backpacks": "#1b6ca8", "Walk (2,3)": "#c4731a", "Both": "#2a8c4a"}

    # Figure 1: mean wait by policy and offset
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    width = 0.25
    for i, off in enumerate((0, 5, 10)):
        vals = [r["mean_wait"] / 60 for t, r in pick("policy") if t[2] == off]
        xs = [j + (i - 1) * width for j in range(len(POLICIES))]
        ax.bar(xs, vals, width, label=f"offset {off} min", color=["#9aa5b1", "#5d7a99", "#1f3d5c"][i])
    ax.set_xticks(range(len(POLICIES)))
    ax.set_xticklabels(list(POLICIES))
    ax.set_ylabel("Mean wait (min)")
    ax.legend(frameon=False)
    save(fig, "fig_wait_policy_offset.pdf")

    # Figure 2: late fraction by policy and offset
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for i, off in enumerate((0, 5, 10)):
        vals = [100 * r["late_frac"] for t, r in pick("policy") if t[2] == off]
        xs = [j + (i - 1) * width for j in range(len(POLICIES))]
        ax.bar(xs, vals, width, label=f"offset {off} min", color=["#9aa5b1", "#5d7a99", "#1f3d5c"][i])
    ax.set_xticks(range(len(POLICIES)))
    ax.set_xticklabels(list(POLICIES))
    ax.set_ylabel("Students late to class (%)")
    ax.legend(frameon=False)
    save(fig, "fig_late_policy_offset.pdf")

    # Figure 3: occupancy sweep
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for pname in POLICIES:
        pts = [(t[2], r["mean_wait"] / 60) for t, r in pick("occ") if t[1] == pname]
        ax.plot(*zip(*pts), marker="o", label=pname, color=colors[pname])
    ax.set_xlabel("Room occupancy (share of rooms in use)")
    ax.set_ylabel("Mean wait (min)")
    ax.legend(frameon=False)
    save(fig, "fig_occupancy_sweep.pdf")

    # Figure 4: queue length over time, baseline vs both
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for pname in ("Baseline", "Both"):
        series = [r for t, r in pick("policy") if t[1] == pname and t[2] == 0][0]["queue_series"]
        length = min(len(s) for s in series)
        xs = [series[0][i][0] / 60 for i in range(length)]
        ys = [sum(s[i][1] for s in series) / len(series) for i in range(length)]
        ax.plot(xs, ys, label=pname, color=colors[pname])
    ax.set_xlabel("Minutes after nominal class end")
    ax.set_ylabel("People waiting")
    ax.legend(frameon=False)
    save(fig, "fig_queue_series.pdf")

    # Figure 5: wait by origin floor, baseline vs both
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    floors = list(ROOMS)
    for i, pname in enumerate(("Baseline", "Both")):
        wf = [r for t, r in pick("policy") if t[1] == pname and t[2] == 0][0]["wait_by_floor"]
        ax.bar([j + (i - 0.5) * 0.4 for j in range(len(floors))], [wf[f] / 60 for f in floors], 0.4,
               label=pname, color=colors[pname])
    ax.set_xticks(range(len(floors)))
    ax.set_xticklabels(floors)
    ax.set_xlabel("Origin floor")
    ax.set_ylabel("Mean wait (min)")
    ax.legend(frameon=False)
    save(fig, "fig_wait_by_floor.pdf")

    # Figure 6: adjacent-floor share
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for pname in ("Baseline", "Both"):
        for off, style in ((0, "-"), (5, "--")):
            pts = [(t[3], r["late_frac"] * 100) for t, r in pick("adj") if t[1] == pname and t[2] == off]
            ax.plot(*zip(*pts), style, marker="o", color=colors[pname], label=f"{pname}, offset {off}")
    ax.set_xlabel("Share of transfers to an adjacent floor")
    ax.set_ylabel("Students late to class (%)")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_adjacent_share.pdf")

    # Figure 7: compliance curves
    fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.0), sharey=True)
    for ax, kind, title in ((axes[0], "bp", "Backpack compliance"), (axes[1], "wd", "Walking compliance")):
        pts = [(t[1], r["mean_wait"] / 60) for t, r in pick(kind)]
        ax.plot(*zip(*pts), marker="o", color="#1b6ca8")
        ax.set_xlabel(title)
    axes[0].set_ylabel("Mean wait (min)")
    save(fig, "fig_compliance.pdf")

    for t, r in pick("policy"):
        print(t[1], t[2], *(round(r[m], 3) for m in METRICS))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
