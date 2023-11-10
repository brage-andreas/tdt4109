X_Str = str  # A, B, .. AA, AB, .. osv.
Y_Str = int  # 1, 2, 3, .. osv (ikke 0-indeksert)
X = int
Y = int

BoardPosition = tuple[X_Str, Y_str]
MatrixPosition = tuple[Y, X]

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

    string = f"{number_to_letter(new_position[0])}{new_position[1]}"

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

        x = self.position[0] + relative_x
        y = self.position[1] + relative_y * self._direction

        return x, y

    def get_horizontal_line_of_sight(
        self, current_x: X, current_y: Y, max_moves: int | None = None
    ) -> list[Position]:
        possible_moves = []

        x_start = current_x - max_moves if max_moves != None else 0
        x_end = current_x + max_moves if max_moves != None else self.board.width

        x_left = current_x - 1, x_start, -1
        x_right = current_x + 1, x_end

        for x in range(*x_left):
            piece_at_position = self.board.at(x, current_y)

            if piece_at_position == None:
                possible_moves.append((x, current_y))
                continue

            if piece_at_position.side != self.side:
                possible_moves.append((x, current_y))

            break

        for x in range(*x_right):
            piece_at_position = self.board.at(x, current_y)

            if piece_at_position == None:
                possible_moves.append((x, current_y))
                continue

            if piece_at_position.side != self.side:
                possible_moves.append((x, current_y))

            break

        return possible_moves

    def get_vertical_line_of_sight(self, current_x: X, current_y: Y) -> list[Position]:
        possible_moves = []

        x_start = current_x - max_moves if max_moves != None else 0
        x_end = current_x + max_moves if max_moves != None else self.board.width

        x_left = current_x - 1, x_start, -1
        x_right = current_x + 1, x_end

        # ↑
        for y in range(y_centre_low, 0, -1):
            piece_at_position = self.board.at(current_x, y)

            if piece_at_position == None:
                possible_moves.append((current_x, y))
                continue

            if piece_at_position.side != self.side:
                possible_moves.append((current_x, y))

            break

        # ↓
        for y in range(y_centre_high, y_end):
            piece_at_position = self.board.at(current_x, y)

            if piece_at_position == None:
                possible_moves.append((current_x, y))
                continue

            if piece_at_position.side != self.side:
                possible_moves.append((current_x, y))

            break

        return possible_moves

    def get_diagonal_line_of_sight(self, current_x: X, current_y: Y) -> list[Position]:
        possible_moves = []

        x_start = current_x - max_moves if max_moves != None else 0
        y_start = current_y - max_moves if max_moves != None else 0
        x_end = current_x + max_moves if max_moves != None else self.board.width
        y_end = current_y + max_moves if max_moves != None else self.board.height

        x_left = current_x - 1, x_start, -1
        x_right = current_x + 1, x_end

        y_up = current_y - 1, y_start, -1
        y_down = current_y + 1, y_end

        for x in range(*x_left):
            for y in range(*y_up):
                piece_at_position = self.board.at(x, y)

                if piece_at_position == None:
                    possible_moves.append((x, y))
                    continue

                if piece_at_position.side != self.side:
                    possible_moves.append((x, y))

                break

        for x in range(*x_left):
            for y in range(*y_down):
                piece_at_position = self.board.at(x, y)

                if piece_at_position == None:
                    possible_moves.append((x, y))
                    continue

                if piece_at_position.side != self.side:
                    possible_moves.append((x, y))

                break

        for x in range(*x_right):
            for y in range(*y_up):
                piece_at_position = self.board.at(x, y)

                if piece_at_position == None:
                    possible_moves.append((x, y))
                    continue

                if piece_at_position.side != self.side:
                    possible_moves.append((x, y))

                break

        for x in range(*x_right):
            for y in range(*y_down):
                piece_at_position = self.board.at(x, y)

                if piece_at_position == None:
                    possible_moves.append((x, y))
                    continue

                if piece_at_position.side != self.side:
                    possible_moves.append((x, y))

                break

        return possible_moves

    def unsafe_move(self, new_position: Position) -> None:
        if self.has_moved == False:
            self.has_moved = True

        board._move(self, new_position)
        self.position = new_position

    def move(self, new_position: Position) -> None:
        return None


class Pawn(Piece):
    def __init__(
        self, board: Board, side: Side, position: Position, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["PAWN"], side, position, has_moved)

    def is_first_move(self) -> bool:
        current_y = 1 if self.side == SIDES["WHITE"] else self.board.height - 2

        return self.position[1] == current_y

    def promote_to_queen(self) -> Queen:
        queen = Queen(self.board, self.side, self.position, has_moved=True)

        self.board.set(self.position, queen)

        return queen

    def get_moves(self):
        possible_moves = [(0, 1), (1, 1), (-1, 1)]

        if self.is_first_move():
            possible_moves.append((0, 2))

        return _validate_moves()


class Board:
    def __init__(self) -> None:
        self.height = BOARD_SIZE
        self.width = BOARD_SIZE

        self.pieces: list[Piece] = []

    def _map(self, x: X, y: Y) -> int:
        return x * self.width + y

    def set(self, position: Position, piece_or_none: Piece | None) -> None:
        """
        Setter en gitt verdi på posisjonen (x, y)
        """

        self.pieces[_map(*position)] = piece

    def at(self, x: X, y: Y) -> Piece | None:
        """
        Henter en brikke fra posisjonen (x, y)
        `None` hvis det ikke er en brikke der
        """

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return None

        return self.pieces[_map(x, y)]
