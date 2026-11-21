"""Reproduce the original 100-state experiment and summarize face-turn counts."""

from random import Random
from statistics import median

from cube import SOLVED, apply_moves, parity, read_state
from solver import PHASES, final_moves, solve


def sample_state(rng):
    corners = list(range(8))
    edges = list(range(12))
    rng.shuffle(corners)
    rng.shuffle(edges)
    if parity(corners) != parity(edges):
        edges[0], edges[1] = edges[1], edges[0]
    twists = [rng.randrange(3) for _ in range(7)]
    flips = [rng.randrange(2) for _ in range(11)]
    twists.append(-sum(twists) % 3)
    flips.append(sum(flips) % 2)
    return read_state(dict(corners=corners, twists=twists, edges=edges, flips=flips))


def main():
    seed, trials = 1701, 100
    rng = Random(seed)
    counts = {name: [] for name, _, _ in PHASES}
    counts["Raw total"] = []
    counts["Final instructions"] = []
    shortened = 0
    for trial in range(1, trials + 1):
        state = sample_state(rng)
        phases = solve(state)
        raw = [move for _, path in phases for move in path]
        if apply_moves(state, raw) != SOLVED:
            raise RuntimeError(f"Raw replay failed on trial {trial}, seed {seed}.")
        final = final_moves(state, phases)  # verifies the simplified replay too
        for name, path in phases:
            counts[name].append(len(path))
        counts["Raw total"].append(len(raw))
        counts["Final instructions"].append(len(final))
        shortened += len(final) < len(raw)

    print(f"{trials}/{trials} states solved and replayed (seed {seed}).")
    print(f"Shorter final instructions on {shortened}/{trials} states.")
    print("Stage | Min | Median | Max")
    for name, values in counts.items():
        print(f"{name} | {min(values)} | {median(values):g} | {max(values)}")


if __name__ == "__main__":
    main()
