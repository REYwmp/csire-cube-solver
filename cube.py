"""A fixed-centre 3×3×3 cube in standard cubie coordinates."""

from operator import itemgetter
from random import Random
from typing import NamedTuple

CORNERS = "URF UFL ULB UBR DFR DLF DBL DRB".split()
EDGES = "UR UF UL UB DR DF DL DB FR FL BL BR".split()
FACES = "URFDLB"


class Cube(NamedTuple):
    corners: tuple
    twists: tuple
    edges: tuple
    flips: tuple


SOLVED = Cube(tuple(range(8)), (0,) * 8, tuple(range(12)), (0,) * 12)


class Turn:
    def __init__(self, effect):
        self.take_corners = itemgetter(*effect.corners)
        self.take_edges = itemgetter(*effect.edges)
        self.twists = effect.twists
        self.flips = effect.flips
        self.twists_corners = any(self.twists)
        self.flips_edges = any(self.flips)

    def __call__(self, state):
        twists = self.take_corners(state.twists)
        flips = self.take_edges(state.flips)
        if self.twists_corners:
            twists = tuple((a + b) % 3 for a, b in zip(twists, self.twists))
        if self.flips_edges:
            flips = tuple(a ^ b for a, b in zip(flips, self.flips))
        return Cube(self.take_corners(state.corners), twists,
                    self.take_edges(state.edges), flips)


def build_turns():
    # Each list gives the OLD position that moves into each NEW position.
    # A corner orientation is the index of its U/D sticker in its position's
    # ordered face triple. An edge is flipped when its sticker order reverses.
    quarter_turns = {
        "U": ("30124567", "00000000", (3,0,1,2,4,5,6,7,8,9,10,11), ()),
        "R": ("41207563", "20011002", (8,1,2,3,11,5,6,7,4,9,10,0), ()),
        "F": ("15230467", "12002100", (0,9,2,3,4,8,6,7,1,5,10,11), (1,5,8,9)),
        "D": ("01235674", "00000000", (0,1,2,3,5,6,7,4,8,9,10,11), ()),
        "L": ("02634157", "01200210", (0,1,10,3,4,5,9,7,8,2,6,11), ()),
        "B": ("01374526", "00120021", (0,1,2,11,4,5,6,10,8,9,3,7), (3,7,10,11)),
    }
    moves = {}
    for face, (corners, twists, edges, flipped) in quarter_turns.items():
        effect = Cube(tuple(map(int, corners)), tuple(map(int, twists)), edges,
                      tuple(int(i in flipped) for i in range(12)))
        quarter = Turn(effect)
        current = SOLVED
        for suffix in ("", "2", "'"):
            current = quarter(current)
            moves[face + suffix] = Turn(current)
    return moves


MOVES = build_turns()


def parse_moves(text):
    moves = text.split()
    for move in moves:
        if move not in MOVES:
            raise ValueError(f"Unknown move {move!r}. Use space-separated turns such as R U2 F'.")
    return moves


def apply_moves(state, moves):
    for move in moves:
        state = MOVES[move](state)
    return state


def inverse(move):
    return move[0] + {"": "'", "'": "", "2": "2"}[move[1:]]


def random_scramble(length, seed=None):
    if length < 0:
        raise ValueError("Scramble length must be nonnegative.")
    rng = Random(seed)
    sequence = []
    previous = ""
    for _ in range(length):
        face = rng.choice([face for face in FACES if face != previous])
        sequence.append(face + rng.choice(("", "'", "2")))
        previous = face
    return sequence


def parity(pieces):
    return sum(a > b for i, a in enumerate(pieces) for b in pieces[i+1:]) % 2


def read_state(data):
    if not isinstance(data, dict) or set(data) != set(Cube._fields):
        raise ValueError("Expected a JSON object with corners, twists, edges and flips.")
    arrays = []
    for key, size in zip(Cube._fields, (8, 8, 12, 12)):
        values = data[key]
        if not isinstance(values, (list, tuple)) or len(values) != size:
            raise ValueError(f"{key} must contain {size} integers.")
        if any(type(value) is not int for value in values):
            raise ValueError(f"{key} must contain only integers.")
        arrays.append(tuple(values))
    cube = Cube(*arrays)
    for pieces in (cube.corners, cube.edges):
        if sorted(pieces) != list(range(len(pieces))):
            raise ValueError("Every corner and edge must appear exactly once in its array.")
    if any(x not in (0, 1, 2) for x in cube.twists) or sum(cube.twists) % 3:
        raise ValueError("Corner twists must be 0–2 and sum to a multiple of three.")
    if any(x not in (0, 1) for x in cube.flips) or sum(cube.flips) % 2:
        raise ValueError("Edge flips must be 0 or 1 and sum to an even number.")
    if parity(cube.corners) != parity(cube.edges):
        raise ValueError("Corner and edge permutations must have matching parity.")
    return cube
