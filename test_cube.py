import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from cube import CORNERS, EDGES, MOVES, SOLVED, Cube, apply_moves, inverse, parse_moves, random_scramble, read_state
from facelets import read_faces
from solver import PHASES, corner_classes, final_moves, solve


def sticker_model(moves):
    # Independent oracle: rotate named stickers in 3D, without using cubie
    # permutations, orientation tables or move application from the solver.
    normals = dict(R=(1, 0, 0), L=(-1, 0, 0), U=(0, 1, 0),
                   D=(0, -1, 0), F=(0, 0, 1), B=(0, 0, -1))
    names = {vector: name for name, vector in normals.items()}

    def rotate(vector, face):
        x, y, z = vector
        a, b, c = normals[face]
        dot = a*x + b*y + c*z
        return (a*dot - b*z + c*y, b*dot - c*x + a*z, c*dot - a*y + b*x)

    result = []
    for labels in (CORNERS, EDGES):
        # Directions of each piece's stickers, in original sticker order.
        directions = [list(label) for label in labels]
        for move in moves:
            for _ in range({"": 1, "2": 2, "'": 3}[move[1:]]):
                for piece, faces in enumerate(directions):
                    if move[0] in faces:
                        directions[piece] = [names[rotate(normals[f], move[0])] for f in faces]
        permutation, orientation = [None]*len(labels), [None]*len(labels)
        slots = {frozenset(label): i for i, label in enumerate(labels)}
        for piece, faces in enumerate(directions):
            slot = slots[frozenset(faces)]
            permutation[slot] = piece
            orientation[slot] = labels[slot].index(faces[0])
        result.extend((tuple(permutation), tuple(orientation)))
    return Cube(*result)


class CubeTests(unittest.TestCase):
    def test_final_moves_across_phases(self):
        for first in MOVES:
            for second in MOVES:
                if first[0] != second[0]:
                    continue
                undo = [inverse(second), inverse(first)]
                state = sticker_model(undo)
                answer = final_moves(state, [("a", [first]), ("b", [second])])
                self.assertLessEqual(len(answer), 1)
                self.assertEqual(sticker_model(undo + answer), SOLVED)
        cascade = [("a", ["R", "U"]), ("b", ["U'", "R'"])]
        self.assertEqual(final_moves(SOLVED, cascade), [])
        state = sticker_model(["R"])
        self.assertEqual(final_moves(state, solve(state)), ["R'"])

    def test_physical_cube_example(self):
        faces = "FLLFUUFUU LLDRRRRRR LBBFFDFFD RRBDDBDDB UUULLDLLD FFRUBBUBB"
        state = read_faces(faces.lower())
        self.assertEqual(state, sticker_model(["F", "R", "U2"]))
        output = subprocess.check_output(
            [sys.executable, str(Path(__file__).with_name("solve_cube.py")), "solve-faces", faces],
            text=True)
        self.assertIn("Solution (3 moves): U2 R' F'", output)
        self.assertIn("Replay: solved", output)

    def test_invalid_stickers(self):
        solved = "".join(f * 9 for f in "URFDLB")
        self.assertEqual(read_faces(solved), SOLVED)
        for pair in ((4, 13), (9, 20), (7, 19)):
            # Swap two centers, mirror a corner, or flip one edge.
            a, b = pair
            stickers = list(solved)
            stickers[a], stickers[b] = stickers[b], stickers[a]
            with self.assertRaises(ValueError):
                read_faces("".join(stickers))
        with self.assertRaises(ValueError):
            read_faces(solved[:-1])

    def test_moves_against_geometric_stickers(self):
        for move in MOVES:
            with self.subTest(move=move):
                self.assertEqual(MOVES[move](SOLVED), sticker_model([move]))
                self.assertEqual(apply_moves(SOLVED, [move, inverse(move)]), SOLVED)
        moves = random_scramble(28, seed=73)
        self.assertEqual(apply_moves(SOLVED, moves), sticker_model(moves))

    def test_corner_cosets(self):
        sizes = Counter(corner_classes().values())
        self.assertEqual(len(sizes), 420)
        self.assertEqual(set(sizes.values()), {96})

    def test_phase_boundaries_and_independent_replay(self):
        for seed in range(10):
            with self.subTest(seed=seed):
                moves = random_scramble(30, seed)
                current = sticker_model(moves)
                all_moves = list(moves)
                for i, ((name, path), (expected_name, allowed, _)) in enumerate(zip(solve(current), PHASES)):
                    self.assertEqual(name, expected_name)
                    self.assertTrue(set(path) <= set(allowed))
                    current = apply_moves(current, path)
                    all_moves.extend(path)
                    for _, _, coordinate in PHASES[:i+1]:
                        self.assertEqual(coordinate(current), coordinate(SOLVED))
                self.assertEqual(sticker_model(all_moves), SOLVED)

    def test_superflip_and_solved(self):
        for start in (SOLVED, SOLVED._replace(flips=(1,)*12)):
            path = [m for _, part in solve(start) for m in part]
            self.assertEqual(apply_moves(start, path), SOLVED)
            if start == SOLVED:
                self.assertEqual(path, [])

    def test_invalid_states(self):
        for bad in (SOLVED._replace(flips=(1,)+(0,)*11),
                    SOLVED._replace(twists=(1,)+(0,)*7),
                    SOLVED._replace(corners=(1,0,2,3,4,5,6,7)),
                    SOLVED._replace(edges=(0,)*12),
                    SOLVED._replace(twists=(True,)+(0,)*7)):
            with self.assertRaises(ValueError):
                read_state(bad._asdict())
        with self.assertRaises(ValueError):
            parse_moves("R sideways")

    def test_state_file_cli(self):
        script = str(Path(__file__).with_name("solve_cube.py"))
        state = subprocess.check_output([sys.executable, script, "state", "R U F2"], text=True)
        self.assertEqual(read_state(json.loads(state)), sticker_model(["R", "U", "F2"]))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cube.json"
            path.write_text(state, encoding="utf-8")
            output = subprocess.check_output([sys.executable, script, "solve-state", str(path)], text=True)
        self.assertIn("Replay: solved", output)


if __name__ == "__main__":
    unittest.main()
