"""Run from this directory with python solve_cube.py --help."""

import argparse
import json
from pathlib import Path

from cube import SOLVED, apply_moves, parse_moves, random_scramble, read_state
from facelets import read_faces
from solver import final_moves, solve


def main():
    parser = argparse.ArgumentParser(description="CSIRE 3×3×3 cube solver renewal")
    commands = parser.add_subparsers(dest="command", required=True)
    by_moves = commands.add_parser("solve", help="solve a scramble written in face turns")
    by_moves.add_argument("moves", help="quoted, space-separated face turns")
    random = commands.add_parser("random", help="generate a scramble and solve it")
    random.add_argument("--length", type=int, default=25)
    random.add_argument("--seed", type=int)
    by_state = commands.add_parser("solve-state", help="solve a cubie-state JSON file")
    by_state.add_argument("file", type=Path)
    by_faces = commands.add_parser("solve-faces", help="solve six faces of sticker labels in U R F D L B order")
    by_faces.add_argument("faces", help="54 center-based sticker labels, optionally separated by spaces")
    export = commands.add_parser("state", help="print a scramble as cubie-state JSON")
    export.add_argument("moves")
    args = parser.parse_args()

    try:
        if args.command == "solve-state":
            state = read_state(json.loads(args.file.read_text(encoding="utf-8-sig")))
        elif args.command == "solve-faces":
            state = read_faces(args.faces)
        else:
            if args.command == "random":
                scramble = random_scramble(args.length, args.seed)
            else:
                scramble = parse_moves(args.moves)
            state = apply_moves(SOLVED, scramble)
            if args.command == "state":
                print(json.dumps(state._asdict(), indent=2))
                return
            print("Scramble:", " ".join(scramble) or "(empty)")
    except (ValueError, OSError) as error:
        parser.error(str(error))

    phases = solve(state)
    for name, path in phases:
        print(f"{name}: {' '.join(path) or '(already satisfied)'}")
    solution = final_moves(state, phases)
    unit = "move" if len(solution) == 1 else "moves"
    print(f"Solution ({len(solution)} {unit}):", " ".join(solution) or "(already solved)")
    print("Replay: solved")


if __name__ == "__main__":
    main()
