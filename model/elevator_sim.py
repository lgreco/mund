"""Discrete-time simulation of one class changeover in Mundelein Center.

One run covers a single 15-minute passing period. Time 0 is the nominal end
of the outgoing class and PASSING is the nominal start of the incoming class,
both in seconds. Two elevator banks serve the building: four cars that reach
floor 9 and two cars that reach floor 14. Cars follow a simple collective
rule and, as observed, do not bypass hall calls when physically full.

All timing constants are assumptions pending a timing study; see Params.
"""
import math
import random
from dataclasses import dataclass

ROOMS = {1: 2, 2: 4, 3: 5, 4: 8, 5: 10, 6: 11, 7: 5, 10: 4, 11: 1, 12: 1, 13: 1, 14: 2}
LOBBY = 1
UPPER_MIN_FLOOR = 10
BANKS = ((4, 9), (2, 14))  # (number of cars, highest floor served)
PASSING = 900
MAX_TIME = 3600
LEAVE_SPREAD = 120
ARRIVE_LO, ARRIVE_MODE, ARRIVE_HI = -600, -180, -60
FLIGHT_SECONDS = 20
ATRIUM_FLIGHT_SECONDS = 40
SAMPLE_EVERY = 10


@dataclass(frozen=True)
class Params:
    p_occ: float = 0.8            # probability a room holds a class in a block
    enroll_lo: int = 15
    enroll_hi: int = 25
    q_next: float = 0.6           # leavers who go on to another class in the building
    adj_share: float = 0.2        # transfers aimed at an adjacent floor
    offset_min: int = 0           # minutes floors 10-14 run ahead of the grid
    walk_down: float = 0.0        # compliance: walk down from floors 2 and 3
    walk_up2: float = 0.0         # compliance: walk up to floor 2
    walk_up3: float = 0.0         # compliance: walk up to floor 3
    adj_stairs: float = 0.0       # extension: stairs for other one-floor trips
    backpack: float = 0.0         # compliance: backpacks held in front
    cap_choices: tuple = (4, 5, 6)
    cap_bonus: int = 2
    t_floor: int = 3              # seconds between adjacent floors
    t_atrium: int = 6             # seconds from floor 1 to 2
    t_door: int = 8               # fixed seconds per stop
    t_pax: float = 1.0            # seconds per boarding or alighting rider


class Passenger:
    __slots__ = ("origin", "dest", "ready", "deadline", "board", "done", "walker")

    def __init__(self, origin, dest, ready, deadline):
        self.origin = origin
        self.dest = dest
        self.ready = ready
        self.deadline = deadline
        self.board = None
        self.done = None
        self.walker = False

    @property
    def direction(self):
        return 1 if self.dest > self.origin else -1


class Car:
    __slots__ = ("top", "floor", "dir", "pax", "state", "timer", "cap", "target")

    def __init__(self, top, floor):
        self.top = top
        self.floor = floor
        self.dir = 0
        self.pax = []
        self.state = "idle"
        self.timer = 0
        self.cap = 0
        self.target = None


def stair_seconds(a, b):
    lo, hi = min(a, b), max(a, b)
    total = 0
    for level in range(lo, hi):
        total += ATRIUM_FLIGHT_SECONDS if level == LOBBY else FLIGHT_SECONDS
    return total


def triangular(rng, lo, mode, hi):
    return rng.triangular(lo, hi, mode)


def pick_room(incoming, floor, adj_share, rng):
    open_rooms = [r for r in incoming if r[2] > 0]
    chosen = None
    if open_rooms:
        pool = open_rooms
        if rng.random() < adj_share:
            near = [r for r in open_rooms if abs(r[0] - floor) == 1]
            if near:
                pool = near
        chosen = rng.choices(pool, weights=[r[2] for r in pool])[0]
        chosen[2] -= 1
    return chosen


def walk_probability(prm, o, d):
    if o in (2, 3) and d < o:
        prob = prm.walk_down
    elif d in (2, 3) and d > o:
        prob = prm.walk_up2 if d == 2 else prm.walk_up3
    elif abs(d - o) == 1 and LOBBY not in (o, d):
        prob = prm.adj_stairs
    else:
        prob = 0.0
    return prob


def build_demand(prm, rng):
    outgoing, incoming = [], []
    for floor, count in ROOMS.items():
        shift = -prm.offset_min * 60 if floor >= UPPER_MIN_FLOOR else 0
        for _ in range(count):
            if rng.random() < prm.p_occ:
                outgoing.append((floor, shift, rng.randint(prm.enroll_lo, prm.enroll_hi)))
            if rng.random() < prm.p_occ:
                incoming.append([floor, PASSING + shift, rng.randint(prm.enroll_lo, prm.enroll_hi)])
    trips = []
    leavers = [(f, shift + rng.uniform(0, LEAVE_SPREAD))
               for f, shift, size in outgoing for _ in range(size)]
    rng.shuffle(leavers)
    for floor, leave_at in leavers:
        room = pick_room(incoming, floor, prm.adj_share, rng) if rng.random() < prm.q_next else None
        if room is not None:
            trips.append(Passenger(floor, room[0], leave_at, room[1]))
        else:
            trips.append(Passenger(floor, LOBBY, leave_at, None))
    for floor, start, seats in incoming:
        for _ in range(seats):
            ready = start + triangular(rng, ARRIVE_LO, ARRIVE_MODE, ARRIVE_HI)
            trips.append(Passenger(LOBBY, floor, ready, start))
    return [p for p in trips if p.origin != p.dest]


def split_walkers(prm, trips, rng):
    riders, walkers = [], []
    for p in trips:
        if rng.random() < walk_probability(prm, p.origin, p.dest):
            p.walker = True
            p.board = p.ready
            p.done = p.ready + stair_seconds(p.origin, p.dest)
            walkers.append(p)
        else:
            riders.append(p)
    return riders, walkers


class World:
    def __init__(self, prm, rng):
        self.prm = prm
        self.rng = rng
        self.waiting = {f: [] for f in range(1, 15)}
        self.cars = []
        self.empty_stops = 0
        self.stops = 0
        self.queue_series = []
        for count, top in BANKS:
            for _ in range(count):
                self.cars.append(Car(top, rng.randint(1, top)))

    def fresh_capacity(self):
        cap = self.rng.choice(self.prm.cap_choices)
        if self.rng.random() < self.prm.backpack:
            cap += self.prm.cap_bonus
        return cap

    def travel_seconds(self, floor, direction):
        gap_low = floor if direction == 1 else floor - 1
        return self.prm.t_atrium if gap_low == LOBBY else self.prm.t_floor

    def can_serve(self, car, p):
        return car.top >= max(p.origin, p.dest)

    def eligible_at(self, car, floor):
        return [p for p in self.waiting[floor] if self.can_serve(car, p)]

    def claimed_by_other(self, car, floor):
        return any(c is not car and c.target == floor for c in self.cars)

    def reasons(self, car):
        f = car.floor
        up = any(p.dest > f for p in car.pax)
        dn = any(p.dest < f for p in car.pax)
        for floor in self.waiting:
            if floor != f and self.waiting[floor] and not self.claimed_by_other(car, floor):
                if self.eligible_at(car, floor):
                    up = up or floor > f
                    dn = dn or floor < f
        return up, dn

    def nearest_call(self, car):
        best, best_gap = None, None
        for floor in self.waiting:
            if floor != car.floor and self.waiting[floor] and not self.claimed_by_other(car, floor):
                if self.eligible_at(car, floor):
                    gap = abs(floor - car.floor)
                    if best is None or gap < best_gap:
                        best, best_gap = floor, gap
        return best

    def depart(self, car):
        up, dn = self.reasons(car)
        if car.dir == 1:
            new = 1 if up else (-1 if dn else 0)
        elif car.dir == -1:
            new = -1 if dn else (1 if up else 0)
        else:
            new = 0
            if car.pax:
                new = 1 if up else (-1 if dn else 0)
            else:
                call = self.nearest_call(car)
                if call is not None:
                    car.target = call
                    new = 1 if call > car.floor else -1
        car.dir = new
        if car.pax:
            car.target = None
        if new == 0:
            car.state = "idle"
            car.target = None
        else:
            car.state = "move"
            car.timer = self.travel_seconds(car.floor, new)

    def serve_floor(self, car, t):
        f = car.floor
        out = [p for p in car.pax if p.dest == f]
        car.pax = [p for p in car.pax if p.dest != f]
        for p in out:
            p.done = t
        candidates = self.eligible_at(car, f)
        if car.pax:
            board_dir = car.dir
        elif candidates:
            board_dir = candidates[0].direction
        else:
            board_dir = 0
        wants = [p for p in candidates if p.direction == board_dir] if board_dir else []
        if not car.pax:
            car.cap = self.fresh_capacity()
        boarded = []
        for p in wants:
            if len(car.pax) + len(boarded) < car.cap:
                boarded.append(p)
        for p in boarded:
            self.waiting[f].remove(p)
            p.board = t
        car.pax.extend(boarded)
        if boarded:
            car.dir = board_dir
        stopped = bool(out or wants)
        if stopped:
            self.stops += 1
            if not out and not boarded:
                self.empty_stops += 1
            car.state = "dwell"
            car.timer = math.ceil(self.prm.t_door + self.prm.t_pax * (len(out) + len(boarded)))
        return stopped

    def step_car(self, car, t):
        if car.state == "idle":
            if not self.serve_floor(car, t):
                self.depart(car)
        elif car.state == "dwell":
            car.timer -= 1
            if car.timer <= 0:
                self.depart(car)
        else:
            car.timer -= 1
            if car.timer <= 0:
                car.floor += car.dir
                if car.target == car.floor:
                    car.target = None
                if not self.serve_floor(car, t):
                    self.depart(car)


def run(prm, seed):
    rng = random.Random(seed)
    trips = build_demand(prm, rng)
    riders, walkers = split_walkers(prm, trips, rng)
    world = World(prm, rng)
    pending = sorted(riders, key=lambda p: p.ready)
    start = int(min([p.ready for p in pending] + [0])) - 5
    nxt, t = 0, start
    while t < MAX_TIME and (nxt < len(pending) or any(world.waiting.values())
                            or any(c.pax for c in world.cars)):
        while nxt < len(pending) and pending[nxt].ready <= t:
            world.waiting[pending[nxt].origin].append(pending[nxt])
            nxt += 1
        for car in world.cars:
            world.step_car(car, t)
        if (t - start) % SAMPLE_EVERY == 0:
            world.queue_series.append((t, sum(len(q) for q in world.waiting.values())))
        t += 1
    return summarize(prm, riders, walkers, world, t)


def percentile(values, q):
    result = 0.0
    if values:
        ordered = sorted(values)
        result = ordered[min(len(ordered) - 1, int(q * len(ordered)))]
    return result


def summarize(prm, riders, walkers, world, end_time):
    served = [p for p in riders if p.done is not None]
    waits = [p.board - p.ready for p in served]
    totals = [p.done - p.ready for p in served]
    with_deadline = [p for p in served + walkers if p.deadline is not None]
    late = [p for p in with_deadline if p.done > p.deadline]
    by_floor = {}
    for f in ROOMS:
        w = [p.board - p.ready for p in served if p.origin == f]
        by_floor[f] = sum(w) / len(w) if w else 0.0
    return {
        "riders": len(riders),
        "walkers": len(walkers),
        "unserved": len(riders) - len(served),
        "mean_wait": sum(waits) / len(waits) if waits else 0.0,
        "p90_wait": percentile(waits, 0.9),
        "max_wait": max(waits) if waits else 0.0,
        "mean_total": sum(totals) / len(totals) if totals else 0.0,
        "late_frac": len(late) / len(with_deadline) if with_deadline else 0.0,
        "empty_stop_frac": world.empty_stops / world.stops if world.stops else 0.0,
        "stops": world.stops,
        "clear_time": end_time,
        "queue_series": world.queue_series,
        "wait_by_floor": by_floor,
    }


def replicate(prm, n, base_seed=0):
    return [run(prm, base_seed + i) for i in range(n)]


def mean_of(results, key):
    return sum(r[key] for r in results) / len(results)


if __name__ == "__main__":
    out = run(Params(), 1)
    print({k: round(v, 3) if isinstance(v, float) else v
           for k, v in out.items() if k not in ("queue_series", "wait_by_floor")})
