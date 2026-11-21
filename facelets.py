"""Read the six faces row by row, viewed from outside the cube."""

from cube import CORNERS, EDGES, FACES, read_state

# Facelet addresses use the face initial and a 1-based row-major index.
# Within each slot the order matches its name in cube.CORNERS or cube.EDGES.
CORNER_SLOTS = ("U9 R1 F3", "U7 F1 L3", "U1 L1 B3", "U3 B1 R3",
                "D3 F9 R7", "D1 L9 F7", "D7 B9 L7", "D9 R9 B7")
EDGE_SLOTS = ("U6 R2", "U8 F2", "U4 L2", "U2 B2", "D6 R8", "D2 F8",
              "D4 L8", "D8 B8", "F6 R4", "F4 L6", "B6 L4", "B4 R6")


def read_faces(text):
    stickers = "".join(text.upper().split())
    if len(stickers) != 54 or any(stickers.count(f) != 9 for f in FACES):
        raise ValueError("Enter nine stickers of each label U R F D L B (54 total).")
    if stickers[4::9] != FACES:
        raise ValueError("Face centers must read U R F D L B in that order.")

    def read_pieces(slots, pieces):
        indices, orientations = [], []
        for slot in slots:
            labels = "".join(stickers[9 * FACES.index(a[0]) + int(a[1]) - 1]
                             for a in slot.split())
            for orientation in range(len(labels)):
                ordered = labels[orientation:] + labels[:orientation]
                if ordered in pieces:
                    indices.append(pieces.index(ordered))
                    orientations.append(orientation)
                    break
            else:
                raise ValueError(f"Impossible sticker order {labels} at {slot}.")
        return indices, orientations

    corners, twists = read_pieces(CORNER_SLOTS, CORNERS)
    edges, flips = read_pieces(EDGE_SLOTS, EDGES)
    return read_state(dict(corners=corners, twists=twists, edges=edges, flips=flips))
