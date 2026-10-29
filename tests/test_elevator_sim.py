"""Verification tests for the elevator simulator.

These check invariants (accounting, determinism, capacity, direction of effects),
not the calibrated numbers, which are assumptions. Run with `make test`.
"""
import os
import random
import sys
import unittest
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "model"))
import elevator_sim as sim  # noqa: E402

LIGHT = sim.Params(p_occ=0.4)  # the main-experiment occupancy
SEEDS = range(5)


def mean_wait(prm):
    """Mean of mean_wait over the shared test seeds."""
    return sim.mean_of([sim.run(prm, s) for s in SEEDS], "mean_wait")


class AccountingTests(unittest.TestCase):
    def test_every_rider_is_served(self):
        for seed in SEEDS:
            out = sim.run(LIGHT, seed)
            self.assertGreater(out["riders"], 0)
            self.assertEqual(out["unserved"], 0)

    def test_empty_building_runs_cleanly(self):
        out = sim.run(replace(LIGHT, p_occ=0.0), 0)
        self.assertEqual(out["riders"], 0)
        self.assertEqual(out["unserved"], 0)
        self.assertEqual(out["mean_wait"], 0.0)

    def test_metrics_are_in_range(self):
        out = sim.run(LIGHT, 0)
        self.assertGreaterEqual(out["mean_wait"], 0.0)
        self.assertLessEqual(out["mean_wait"], out["max_wait"])
        self.assertLessEqual(out["p90_wait"], out["max_wait"])
        self.assertTrue(0.0 <= out["late_frac"] <= 1.0)
        self.assertLess(out["clear_time"], sim.MAX_TIME)


class ReproducibilityTests(unittest.TestCase):
    def test_same_seed_same_result(self):
        self.assertEqual(sim.run(LIGHT, 3), sim.run(LIGHT, 3))

    def test_different_seeds_differ(self):
        self.assertNotEqual(sim.run(LIGHT, 1)["mean_wait"], sim.run(LIGHT, 2)["mean_wait"])


class CapacityTests(unittest.TestCase):
    def test_fresh_capacity_without_backpacks(self):
        world = sim.World(LIGHT, random.Random(0))
        caps = {world.fresh_capacity() for _ in range(200)}
        self.assertTrue(caps <= set(LIGHT.cap_choices))

    def test_fresh_capacity_with_full_compliance(self):
        prm = replace(LIGHT, backpack=1.0)
        world = sim.World(prm, random.Random(0))
        caps = {world.fresh_capacity() for _ in range(200)}
        self.assertTrue(caps <= {c + prm.cap_bonus for c in prm.cap_choices})


class BuildingTests(unittest.TestCase):
    def test_floor_counts_match_the_established_facts(self):
        self.assertEqual(sum(sim.ROOMS.values()), 54)
        self.assertEqual(len(sim.ROOMS), 12)
        self.assertNotIn(8, sim.ROOMS)
        self.assertNotIn(9, sim.ROOMS)

    def test_banks(self):
        self.assertEqual(sum(count for count, _ in sim.BANKS), 6)
        self.assertEqual(max(top for _, top in sim.BANKS), 14)

    def test_percentile(self):
        self.assertEqual(sim.percentile([], 0.9), 0.0)
        self.assertEqual(sim.percentile([5], 0.9), 5)
        self.assertEqual(sim.percentile(list(range(10)), 0.9), 9)


class DirectionOfEffectTests(unittest.TestCase):
    def test_backpacks_reduce_waiting(self):
        self.assertLess(mean_wait(replace(LIGHT, backpack=1.0)), mean_wait(LIGHT))

    def test_walking_moves_riders_to_the_stairs(self):
        prm = replace(LIGHT, walk_down=1.0, walk_up2=1.0, walk_up3=1.0)
        base, walk = sim.run(LIGHT, 0), sim.run(prm, 0)
        self.assertGreater(walk["walkers"], base["walkers"])
        self.assertLess(walk["riders"], base["riders"])

    def test_more_occupancy_means_more_riders(self):
        low, high = sim.run(replace(LIGHT, p_occ=0.2), 0), sim.run(replace(LIGHT, p_occ=0.8), 0)
        self.assertGreater(high["riders"], low["riders"])


if __name__ == "__main__":
    unittest.main()
