# Mundelein Elevator Demand: Problem Statement and First Estimates

Scope: classes held before 4 PM (MWF 8:15-3:35, TR 8:30-3:45). See `scheduling_grid.md`.
Classroom counts: see `classrooms_per_floor.md` (54 classrooms; 9 on floors 10-14).

## Facts

- Two elevator banks: 4 cars and 2 cars. Only the 2-car bank reaches above floor 9; it serves all floors.
- Car capacity: 3000 lbs (about 17-20 riders by weight). Cars typically leave with 4-6 riders, so space, not weight, is the limit.
- Classrooms seat 30-35; enrollment is often 15-25.
- Floor 1 is an atrium lobby. Stairs from floor 1 to 2 feel like 2 standard flights; students leave the building from the lobby.
- Long lines form in the 10 minutes before each class start.
- Down trips: a car leaves floor 9 and is physically full by floor 6 but still stops at floors 5, 4, 3 and 2, because it is not full by weight.

## Behavior changes in scope

1. Walk down (and, where reasonable, up) for floors 2 and 3 (9 rooms, about 180 students at 20 per class).
2. Remove backpacks and hold them in front: about 2 more riders per car (6-8 instead of 4-6), a 33-50% capacity gain.

Out of scope: courtesy rules, load-bypass settings, down-peak modes.

## First-cut estimates (illustrative; elevator timings are guesses)

| Scenario | Load vs. today |
|---|---|
| Backpacks only | 67-75% |
| Backpacks + walk to floor 2 only | 61-68% |
| Backpacks + walk to floors 2 and 3 | 53-60% |

Walking down is easy and targets the empty-stop problem; walking up is harder (floor 3 especially).

## Open questions

- Are floors above the atrium standard height?
- What is the up/down split at changeover?
- Timed trips: round-trip time and seconds per stop.
