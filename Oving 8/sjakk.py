X = str
Y = int
Position = tuple[X, Y]

Side = 1 | 0
SIDES = {"WHITE": 0, "BLACK": 1}

Piece_Id = 5 | 4 | 3 | 2 | 1 | 0
PIECE_IDS = {"BISHOP": 0, "KING": 1, "KNIGHT": 2, "PAWN": 3, "QUEEN": 4, "ROOK": 5}

Piece_String = "♗" | "♔" | "♘" | "♙" | "♕" | "♖" | "♝" | "♚" | "♞" | "♟" | "♛" | "♜"
PIECE_STRINGS = {
    SIDES["BLACK"]: {
        PIECE_IDS["BISHOP"]: "♝",
        PIECE_IDS["KING"]: "♚",
        PIECE_IDS["KNIGHT"]: "♞",
        PIECE_IDS["PAWN"]: "♟",
        PIECE_IDS["QUEEN"]: "♛",
        PIECE_IDS["ROOK"]: "♜",
    },
    SIDES["WHITE"]: {
        PIECE_IDS["BISHOP"]: "♗",
        PIECE_IDS["KING"]: "♔",
        PIECE_IDS["KNIGHT"]: "♘",
        PIECE_IDS["PAWN"]: "♙",
        PIECE_IDS["QUEEN"]: "♕",
        PIECE_IDS["ROOK"]: "♖",
    },
}

Notation_Key = "B" | "K" | "N" | "P" | "Q" | "R"

NOTATIONS = {
    CAPTURE: "x",
    CHECK: "+",
    CHECKMATE: "#",
    KINGSIDE_CASTLE: "O-O",
    PROMOTION: "=",
    QUEENSIDE_CASTLE: "O-O-O",
}

NUMBER_OF_LETTERS = 26
UNICODE_A = 65

# Disse støttes ikke å endre
# er her bare for å unngå magiske tall
NUMBER_OF_PLAYERS = 2
BOARD_SIZE = 8
# ---


def number_to_letter(number: int) -> str:
    """
    Omgjør et tall til en (eller flere) bokstav(er):
      0 -> A
      1 -> B
      2 -> C
      ...
      25 -> Z
      26 -> AA
      27 -> AB
      ...
      51 -> AZ
      52 -> BA
      53 -> BB
    """

    mutable_number = number + 1  # ellers blir det 0 -> A, 1 -> B, 2 -> C, osv.
    string = ""

    while mutable_number > 0:
        mutable_number -= 1

        unicode = UNICODE_A + (mutable_number % NUMBER_OF_LETTERS)
        string = chr(unicode) + string

        mutable_number //= 26

    return string


def letter_to_number(letter: str) -> str:
    """
    Omgjør en (eller flere) bokstav(er) til et tall:
      A  -> 0
      B  -> 1
      C  -> 2
      ...
      Z  -> 25
      AA -> 26
      AB -> 27
      ...
      AZ -> 51
      BA -> 52
      BB -> 53
    """

    number = 0

    for letter_ in letter:
        number_from_unicode = ord(letter_) - UNICODE_A
        number = number * NUMBER_OF_LETTERS + number_from_unicode

    return number


def get_data_from_piece_string(piece_string: Piece_String) -> tuple[Piece_Id, Side]:
    for side in PIECE_STRINGS:
        for piece_id in PIECE_STRINGS[side]:
            if PIECE_STRINGS[side][piece_id] == piece_string:
                return (piece_id, side)


def generate_algebraic_notation(
    piece_key: Notation_Key,
    new_position: Position,
    old_position: Position | None = None,
    capture=False,
    kingside_castle=False,
    queenside_castle=False,
    check=False,
    checkmate=False,
    promotion: Notation_Key | None = None,
) -> str:
    # Denne er ikke perfekt men duger
    # F.eks. den vil ikke skille om du har to tårn som kan flyttes til samme position
    # siden det var for komplisert for en unødvendig feature

    if kingside_castle:
        return NOTATIONS[KINGSIDE_CASTLE]

    if queenside_castle:
        return NOTATIONS[QUEENSIDE_CASTLE]

    string = ""

    if piece_key != "P":
        string += piece_key

    if capture:
        string += NOTATIONS[CAPTURE]

    string = f"{number_to_letter(new_position[1])}{new_position[0] + 1}"

    if promotion:
        string += NOTATIONS[PROMOTION] + promotion

    if check:
        string += NOTATIONS[CHECK]

    if checkmate:
        string += NOTATIONS[CHECKMATE]

    return string


class Piece:
    def __init__(
        self,
        board: Board,
        piece_id: int,
        side: int,
        position: Position,
        has_moved=False,
    ) -> None:
        self._direction = 1 if self.side == SIDES["WHITE"] else -1

        self.has_moved = has_moved
        self.piece_id = piece_id
        self.position = position
        self.board = board
        self.side = side

        self.string = PIECE_STRINGS[side][piece_id]

    def __str__(self) -> str:
        return self.string

    def _translate(self, relative_x: X, relative_y: Y) -> Position:
        """
        Skriver om en relativ posisjon til en absolutt posisjon.
          _translate(1, 0) -> 1 til høyre
          _translate(0, 1) -> 1 mot motstanderens side
        """
        x_numerical = letter_to_number(self.position[0]) + relative_x
        x = number_to_letter(x_numerical)

        y = self.position[1] + relative_y * self._direction

        return x, y

    def _get_unsafe_horizontal_moves(
        self, current_x: X, current_y: Y
    ) -> list[Position]:
        possible_moves = []

        for x in range(0, board.width):
            if x == letter_to_number(current_x):
                continue

            possible_moves.append((number_to_letter(x), current_y))

        return possible_moves

    def get_horizontal_moves(self, current_x: X, current_y: Y) -> list[Position]:
        possible_moves = self._get_unsafe_horizontal_moves(current_x, current_y)
        # todo

    def _get_unsafe_vertical_moves(
        self, current_x: X, current_y: Y
    ) -> list[Position]:
        possible_moves = []

        for y in range(0, board.height):
            if y == current_y:
                continue

            possible_moves.append((current_x, y))

        return possible_moves

    # logikk fra https://stackoverflow.com/a/29567034
    def _get_unsafe_diagonal_moves(
        self, current_x: X, current_y: Y
    ) -> list[Position]:
        possible_moves = []

        for x in range(0, board.width):
            if x == letter_to_number(current_x):
                continue

            for y in range(0, board.height):
                if abs(x - letter_to_number(current_x)) == abs(y - current_y):
                    possible_moves.append((number_to_letter(x), y))

        return possible_moves

    """ def _validate_moves(
        self, moves_to_check: list[Position]
    ) -> list[Position]:
        possible_moves = []

        for x, y in moves_to_check:
            new_position = self._translate(x, y)
            piece_in_new_position = board.at(new_position)

            if piece_in_new_position == None or piece_in_new_position.side != self.side:
                possible_moves.append(new_position)

        return possible_moves """

    def unsafe_move(self, new_position: Position) -> None:
        if self.has_moved == False:
            self.has_moved = True

        board._move(self, new_position)
        self.position = new_position

    def move(self, new_position: Position) -> None:


class Pawn(Piece):
    def __init__(self, board: Board, side: Side, position: Position) -> None:
        super().__init__(board, PIECE_IDS["PAWN"], side, position)

    def is_first_move(self) -> bool:
        current_y = 1 if self.side == SIDES["WHITE"] else self.board.height - 2

        return self.position[1] == current_y

    def promote_to_queen(self, board: Board) -> Queen:
        # todo
        return Queen(self.side, self.position)

    def get_moves():
        possible_moves = [(0, 1), (1, 1), (-1, 1)]

        if self.is_first_move():
            possible_moves.append((0, 2))

        return _validate_moves()


class Board:
    def __init__(self) -> None:
        self.height = BOARD_SIZE
        self.width = BOARD_SIZE

        self.pieces: list[Piece] = []

    def _get_pieces_index(self, x: X, y: Y) -> int:
        return letter_to_number(x) * self.width + y

    def _move(self, piece: Piece, new_position: Position) -> None:
        """
        Flytter en brikke til en ny posisjon og oppdaterer brikken
        Unsafe -- sjekk om trekket er gyldig først
        """

        old_position = piece.position
        piece.position = new_position

        self.pieces[_get_pieces_index(*old_position)] = None
        self.pieces[_get_pieces_index(*new_position)] = piece

    def at(self, x: X, y: Y) -> Piece | None:
        """
        Henter en brikke fra posisjonen (x, y)
        `None` hvis det ikke er en brikke der
        """

        if not 0 <= letter_to_number(x) < self.width or not 0 <= y < self.height:
            return None

        return self.pieces[_get_pieces_index(x, y)]
