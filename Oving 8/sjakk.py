PIECE_IDS = {
    "BISHOP": 0,
    "KING": 1,
    "KNIGHT": 2,
    "PAWN": 3,
    "QUEEN": 4,
    "TOWER": 5
}

PIECE_STRINGS = {
    0: {
        0: "♗",
        1: "♔",
        2: "♘",
        3: "♙",
        4: "♕",
        5: "♖"
    },
    1: {
        0: "♝",
        1: "♚",
        2: "♞",
        3: "♟",
        4: "♛",
        5: "♜"
    }
}

SIDES = {"WHITE": 0, "BLACK": 1}

POSITION = tuple[int, int]


class Piece:

    def __init__(self,
                 piece_id: int,
                 side: int,
                 position: POSITION,
                 is_alive: bool = True) -> None:
        self.piece_id = piece_id
        self.side = side
        self.position = position
        self.is_alive = is_alive
        self.string = PIECE_STRINGS[side][piece_id]


class Board:
    pieces: list[Piece] = []

    def __init__(self, height_y: int, width_x: int) -> None:
        self.height = height_y
        self.width = width_x

    def get_as_matrix(self):
        pieces_copy = self.pieces
        matrix: list[list[Piece | None]] = [[None for _ in range(self.width)] for _ in range(self.height)]

        for y in range(0, self.height):
            for x in range(0, self.width):
                for piece in pieces_copy:
                    if piece.position[0] == x and piece.position[1] == y:
                        matrix[y][x] = piece

    def draw(self):
        