from typing import Union
from re import sub as re_sub

X_Str = str  # A, B, .. AA, AB, .. osv.
Y_Str = int  # 1, 2, 3, .. osv (ikke 0-indeksert)
X = int
Y = int

BoardPosition = str  # X_StrY_Str, "A4", "B2", osv.
MatrixPosition = tuple[Y, X]

Side = 1 | 0
SIDES = {"WHITE": 0, "BLACK": 1}

Any_Piece = Union["Bishop", "King", "Knight", "Pawn", "Queen", "Rook"]

Piece_Id = 5 | 4 | 3 | 2 | 1 | 0
PIECE_IDS = {
    "BISHOP": 0,
    "B": 0,
    "KING": 1,
    "K": 1,
    "KNIGHT": 2,
    "N": 2,
    "PAWN": 3,
    "P": 3,
    "QUEEN": 4,
    "Q": 4,
    "ROOK": 5,
    "R": 5,
    "PASSANT": 6,
    "G": 6,  # Ghost
}

PIECE_STRINGS = {
    SIDES["BLACK"]: {
        PIECE_IDS["BISHOP"]: "♝",
        PIECE_IDS["KING"]: "♚",
        PIECE_IDS["KNIGHT"]: "♞",
        PIECE_IDS["PAWN"]: "♟",
        PIECE_IDS["QUEEN"]: "♛",
        PIECE_IDS["ROOK"]: "♜",
        PIECE_IDS["PASSANT"]: "",
    },
    SIDES["WHITE"]: {
        PIECE_IDS["BISHOP"]: "♗",
        PIECE_IDS["KING"]: "♔",
        PIECE_IDS["KNIGHT"]: "♘",
        PIECE_IDS["PAWN"]: "♙",
        PIECE_IDS["QUEEN"]: "♕",
        PIECE_IDS["ROOK"]: "♖",
        PIECE_IDS["PASSANT"]: "",
    },
}

ALGEBRAIC_NOTATION = {
    "CAPTURE": "x",
    "CHECK": "+",
    "CHECKMATE": "#",
    "KINGSIDE_CASTLE": "O-O",
    "PROMOTION": "=",
    "QUEENSIDE_CASTLE": "O-O-O",
}

DEFAULT_FORSYTH_EDWARDS_NOTATION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

NUMBER_OF_LETTERS = 26
UNICODE_A = 65

# Disse støttes ikke å endre
# er her bare for å unngå magiske tall
NUMBER_OF_PLAYERS = 2
BOARD_SIZE = 8
# ---


def clear_console() -> None:
    print("\033c", end="")


def black_background(string: str) -> str:
    return f"\x1b[0;37;40m{string}\x1b[0m"


def white_background(string: str) -> str:
    return f"\x1b[0;30;47m{string}\x1b[0m"


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
    piece_key: str,
    new_position: MatrixPosition,
    old_position: MatrixPosition | None = None,
    capture=False,
    kingside_castle=False,
    queenside_castle=False,
    check=False,
    checkmate=False,
    promotion: str | None = None,
) -> str:
    # Denne er ikke perfekt men duger
    # F.eks. den vil ikke skille om du har to tårn som kan flyttes til samme position
    # siden det var for komplisert for en unødvendig feature

    if kingside_castle:
        return ALGEBRAIC_NOTATION[KINGSIDE_CASTLE]

    if queenside_castle:
        return ALGEBRAIC_NOTATION[QUEENSIDE_CASTLE]

    string = ""

    if piece_key != "P":
        string += piece_key

    if capture:
        string += ALGEBRAIC_NOTATION[CAPTURE]

    string = f"{number_to_letter(new_position[0])}{new_position[1]}"

    if promotion:
        string += ALGEBRAIC_NOTATION[PROMOTION] + promotion

    if check:
        string += ALGEBRAIC_NOTATION[CHECK]

    if checkmate:
        string += ALGEBRAIC_NOTATION[CHECKMATE]

    return string


class Board:
    def __init__(
        self, forsyth_edwards_notation=DEFAULT_FORSYTH_EDWARDS_NOTATION
    ) -> None:
        self.height = BOARD_SIZE
        self.width = BOARD_SIZE

        self.pieces: Union[Any_Piece, None] = []

    def __str__(self) -> str:
        string = (
            "  " + " ".join([number_to_letter(x) for x in range(0, self.width)]) + "\n"
        )

        prefix = [f"{x + 1} " for x in range(0, self.height)]

        for y in range(0, self.height):
            string += prefix[y]

            for x in range(0, self.width):
                piece = self.get(x, y)
                x_is_even = x % 2 == 0
                y_is_even = y % 2 == 0

                is_white_square = (x_is_even and y_is_even) or (
                    not x_is_even and not y_is_even
                )

                if is_white_square:
                    string += white_background(f"{piece or ' '} ")
                else:
                    string += black_background(f"{piece or ' '} ")

            string += "\n"

        return string

    def parse_position(
        self, posistion: BoardPosition | MatrixPosition
    ) -> MatrixPosition:
        if isinstance(posistion, tuple):
            return posistion

        if posistion == ALGEBRAIC_NOTATION["KINGSIDE_CASTLE"]:
            return (6, 0)

        if posistion == ALGEBRAIC_NOTATION["QUEENSIDE_CASTLE"]:
            return (2, 0)

        if len(posistion) != 2:
            raise ValueError("posistion må være en string med lengde 2")

        x, y = posistion

        if x.isalpha():
            x = letter_to_number(x)

        if not y.isdigit():
            raise ValueError("y må være et tall")

        return x, int(y) - 1

    def translate(self, x: X, y: Y) -> int:
        return y * self.width + x

    def position_exists(self, x: X, y: Y) -> bool:
        x_high = self.width - 1
        y_high = self.height - 1

        return 0 <= x <= x_high and 0 <= y <= y_high

    def set(
        self, position: MatrixPosition, piece_or_none: Union[Any_Piece, None]
    ) -> None:
        """
        Setter en gitt verdi på posisjonen (x, y)
        """

        self.pieces[self.translate(*position)] = piece_or_none

    def get(self, x: X, y: Y) -> Union[Any_Piece, None]:
        """
        Henter en brikke fra index [y][x]
        `None` hvis det ikke er en brikke der
        """

        if not self.position_exists(x, y):
            return None

        piece = self.pieces[self.translate(x, y)]

        return piece

    def at(self, xy: str) -> Union[Any_Piece, None]:
        """
        Henter en brikke fra posisjonen (x, y)
        `None` hvis det ikke er en brikke der
        """

        return self.get(*self.parse_position(xy))


class Piece:
    def __init__(
        self,
        board: Board,
        piece_id: int,
        side: int,
        position: MatrixPosition,
        has_moved=False,
    ) -> None:
        self.has_moved = has_moved
        self.piece_id = piece_id
        self.position = position
        self.board = board
        self.side = side

        self._direction = -1 if self.side == SIDES["WHITE"] else 1
        self.string = PIECE_STRINGS[side][piece_id]

    def __str__(self) -> str:
        return self.string

    def _translate_move(self, move: MatrixPosition) -> MatrixPosition:
        relative_x = self.position[0] + move[0]
        relative_y = self.position[1] + move[1] * self._direction

        return relative_x, relative_y

    def _validate_moves(
        self, relative_moves: list[MatrixPosition]
    ) -> list[MatrixPosition]:
        """
        Filtrerer til bare trekk innenfor brettet som ikke har en brikke av samme side
        Tar ikke hensyn til line-of-sight eller om det er et lovlig trekk for brikken
        """

        valid_positions: set[MatrixPosition] = set()

        for relative_move in relative_moves:
            x, y = self._translate_move(relative_move)

            if not self.board.position_exists(x, y):
                continue

            piece_at_position = self.board.get(x, y)

            if piece_at_position == None or piece_at_position.side != self.side:
                valid_positions.add((x, y))

        return list(valid_positions)

    def get_horizontal_line_of_sight(
        self, current_x: X, current_y: Y, max_moves: int | None = None
    ) -> list[MatrixPosition]:
        positions: set[MatrixPosition] = set()

        x_start = current_x - max_moves if max_moves != None else 0
        x_end = current_x + max_moves if max_moves != None else self.board.width

        x_left = current_x - 1, x_start, -1
        x_right = current_x + 1, x_end

        for x in range(*x_left):
            piece_at_position = self.board.get(x, current_y)

            if piece_at_position == None:
                positions.add((current_x - x, 0))
                continue

            if piece_at_position.side != self.side:
                positions.add((current_x - x, 0))

            break

        for x in range(*x_right):
            piece_at_position = self.board.get(x, current_y)

            if piece_at_position == None:
                positions.add((current_x - x, 0))
                continue

            if piece_at_position.side != self.side:
                positions.add((current_x - x, 0))

            break

        return list(positions)

    def get_vertical_line_of_sight(
        self, current_x: X, current_y: Y, max_moves: int | None = None
    ) -> list[MatrixPosition]:
        positions: set[MatrixPosition] = set()

        y_start = current_y - max_moves if max_moves != None else 0
        y_end = current_y + max_moves if max_moves != None else self.board.height

        y_up = current_y - 1, y_start, -1
        y_down = current_y + 1, y_end

        for y in range(*y_up):
            piece_at_position = self.board.get(current_x, y)

            if piece_at_position == None:
                positions.add((0, current_y + y * self._direction))
                continue

            if piece_at_position.side != self.side:
                positions.add((0, current_y + y * self._direction))

            break

        for y in range(*y_down):
            piece_at_position = self.board.get(current_x, y)

            print(current_y + y * self._direction)

            if piece_at_position == None:
                positions.add((0, current_y + y * self._direction))
                continue

            if piece_at_position.side != self.side:
                positions.add((0, current_y + y * self._direction))

            break

        return list(positions)

    def get_diagonal_line_of_sight(
        self, current_x: X, current_y: Y, max_moves=None
    ) -> list[MatrixPosition]:
        positions: set[MatrixPosition] = set()

        x_limit = self.board.width
        y_limit = self.board.height

        def check_and_add_position(
            current_position: MatrixPosition, position: MatrixPosition
        ) -> bool:
            current_x, current_y = current_position
            x, y = position

            if 0 <= x < x_limit and 0 <= y < y_limit:
                piece_at_position = self.board.get(x, y)

                if piece_at_position is None:
                    positions.add((x - current_x, (y - current_y) * self._direction))
                    return True
                elif piece_at_position.side != self.side:
                    positions.add((x - current_x, (y - current_y) * self._direction))

            return False

        for x_dir, y_dir in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            x = current_x
            y = current_y

            for _ in range(
                max_moves if max_moves is not None else max(x_limit, y_limit)
            ):
                x += x_dir * self._direction
                y += y_dir * self._direction

                if not check_and_add_position((current_x, current_y), (x, y)):
                    break

        return list(positions)

    def get_moves(self):
        raise NotImplementedError("get_moves må implementeres i child ")

    def move(self, new_position: MatrixPosition) -> None:
        if self.has_moved == False:
            self.has_moved = True

        old_position = self.position

        self.board.set(new_position, self)
        self.position = new_position

        if self.piece_id == PIECE_IDS["PAWN"]:
            if new_position[1] == 0 or new_position[1] == self.board.height - 1:
                self.promote_to_queen()


class Bishop(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["BISHOP"], side, position, has_moved)

    def get_moves(self):
        positions = set(self.get_horizontal_line_of_sight(*self.position))

        return self._validate_moves(positions)


class King(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["KING"], side, position, has_moved)

    def get_moves(self):
        positions = set(
            [
                *self.get_horizontal_line_of_sight(*self.position, max_moves=1),
                *self.get_vertical_line_of_sight(*self.position, max_moves=1),
                *self.get_diagonal_line_of_sight(*self.position, max_moves=1),
            ]
        )

        return self._validate_moves(positions)


class Knight(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["KNIGHT"], side, position, has_moved)

    def get_moves(self):
        positions = set(
            [(-2, 1), (-2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2), (2, 1), (2, -1)]
        )

        return self._validate_moves(positions)


class Queen(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["QUEEN"], side, position, has_moved)

    def get_moves(self):
        positions = set(
            [
                *self.get_horizontal_line_of_sight(*self.position),
                *self.get_vertical_line_of_sight(*self.position),
                *self.get_diagonal_line_of_sight(*self.position),
            ]
        )

        print(self.get_horizontal_line_of_sight(*self.position))

        return self._validate_moves(positions)


class Pawn(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["PAWN"], side, position, has_moved)

    def get_moves(self):
        positions = set([(0, 1)])

        if not self.has_moved:
            positions.add((0, 2))

        top_left = self.board.get(*self._translate_move((-1, 1)))
        top_right = self.board.get(*self._translate_move((1, 1)))

        if top_left != None and top_left.side != self.side:
            positions.add((-1, 1))

        if top_right != None and top_right.side != self.side:
            positions.add((1, 1))

        return self._validate_moves(positions)

    def promote_to_queen(self) -> Queen:
        queen = Queen(self.board, self.side, self.position, has_moved=True)

        self.board.set(self.position, queen)

        return queen


class Rook(Piece):
    def __init__(
        self, board: Board, side: Side, position: MatrixPosition, has_moved=False
    ) -> None:
        super().__init__(board, PIECE_IDS["ROOK"], side, position, has_moved)

    def get_moves(self):
        positions = set(
            [
                *self.get_vertical_line_of_sight(*self.position),
                *self.get_diagonal_line_of_sight(*self.position),
            ]
        )

        return self._validate_moves(positions)


class Passant(Piece):
    def __init__(
        self,
        board: Board,
        side: Side,
        position: MatrixPosition,
        pawn: Pawn,
        dies_on_half_turn: int,
    ) -> None:
        super().__init__(board, PIECE_IDS["PASSANT"], side, position, False)
        self.dies_on_half_turn = dies_on_half_turn
        self.parent = pawn


PIECE_CLASSES = {
    PIECE_IDS["BISHOP"]: Bishop,
    PIECE_IDS["KING"]: King,
    PIECE_IDS["KNIGHT"]: Knight,
    PIECE_IDS["PAWN"]: Pawn,
    PIECE_IDS["QUEEN"]: Queen,
    PIECE_IDS["ROOK"]: Rook,
    PIECE_IDS["PASSANT"]: Passant,
}


class Game:
    def __init__(
        self, forsyth_edwards_notation=DEFAULT_FORSYTH_EDWARDS_NOTATION
    ) -> None:
        self.board = Board()
        self.turn = 0

        self.board.pieces = self.load_pieces(forsyth_edwards_notation)

    def _handle_input(self, input: str) -> str:
        mutable_input = re_sub(r"\s+", "", input.upper())

        if mutable_input == "quit" or mutable_input == "exit":
            exit()

        return mutable_input

    def _get_piece_input(self) -> Any_Piece:
        piece = None

        while piece == None:
            raw_position_input = self._handle_input(
                input("Hvilken brikke vil du flytte? ")
            )

            try:
                position_input = self.board.parse_position(raw_position_input)
            except ValueError as e:
                print(f"Ugyldig input: '{e}'. Vennligst prøv igjen.")
                continue

            raw_piece = self.board.at(position_input)

            x_str = number_to_letter(position_input[0])
            position_str = f"{x_str}{position_input[1] + 1}"

            if raw_piece == None:
                print(
                    f"Det er ingen brikke i posisjonen {position_str}. Vennligst prøv igjen."
                )
                continue

            if raw_piece.side == self.turn % NUMBER_OF_PLAYERS:
                print(
                    f"Brikken i posisjonen {position_str} er ikke din. Vennligst prøv igjen."
                )
                continue

            piece = raw_piece

        return piece

    def _get_move_input(self, piece: Any_Piece) -> MatrixPosition:
        available_moves = []
        move = None

        for available_move in piece.get_moves():
            available_moves.append(
                f"{number_to_letter(available_move[0])}{available_move[1] + 1}"
            )

        print(f"- Du kan flytte til: {', '.join(available_moves)}")

        while move == None:
            raw_move_input = self._handle_input(
                input(
                    f"Hvor vil du flytte {piece} ({number_to_letter(piece.position[0])}{piece.position[1] + 1})?"
                )
            )

            try:
                move_input = self.board.parse_position(raw_move_input)
            except ValueError as e:
                print("Ugyldig input: '{e}'. Vennligst prøv igjen.")
                continue

            if move_input not in piece.get_moves():
                print(
                    f"Du kan ikke flytte {piece} til {raw_move_input}. Vennligst prøv igjen."
                )
                continue

            move = move_input

        return move

    def create_piece_from_forsyth_edwards_notation_key(
        self, piece: str, position: MatrixPosition
    ) -> Any_Piece:
        piece_id = PIECE_IDS[piece.upper()]
        side = SIDES["BLACK"] if piece.islower() else SIDES["WHITE"]

        piece_class = PIECE_CLASSES.get(piece_id)

        return piece_class(self.board, side, position)

    def load_pieces(self, forsyth_edwards_notation: str) -> list[Any_Piece | None]:
        pieces: list[Piece | None] = []
        rows = forsyth_edwards_notation.split("/")

        for y, row in enumerate(rows):
            x = 0

            for key in row:
                if key.isdigit():
                    pieces.extend([None for _ in range(0, int(key))])
                    x += int(key)

                    continue

                pieces.append(
                    self.create_piece_from_forsyth_edwards_notation_key(key, (x, y))
                )

                x += 1

        return pieces

    def next_turn(self):
        self.turn += 1

        clear_console()
        print(self.board, end="\n\n")

        chosen_piece = self._get_piece_input()
        original_position = number_to_letter(chosen_piece.position[0]) + str(
            chosen_piece.position[1] + 1
        )

        clear_console()
        print(self.board, end="\n\n")

        chosen_move = self._get_move_input(chosen_piece)

        if chosen_piece.piece_id == PIECE_IDS["PAWN"]:
            if chosen_move == chosen_piece._translate_move((0, 2)):
                passant_position = chosen_piece._translate_move((0, 1))
                passant = Passant(
                    self.board,
                    chosen_piece.side,
                    passant_position,
                    chosen_piece,
                    self.turn + 1,
                )

                self.board.set(passant_position, passant)

        piece_at_chosen_move = self.board.get(*chosen_move)

        if (
            piece_at_chosen_move != None
            and piece_at_chosen_move.piece_id == PIECE_IDS["PASSANT"]
        ):
            self.board.set(piece_at_chosen_move.parent.position, None)

        old_position = chosen_piece.position
        chosen_piece.move(chosen_move)
        self.board.set(old_position, None)

        clear_console()
        print(self.board, end="\n\n")
        print(
            f"You moved {original_position} to {number_to_letter(chosen_move[0])}{chosen_move[1] + 1}"
        )

        passant_pieces = [
            piece
            for piece in self.board.pieces
            if isinstance(piece, Passant) and piece.dies_on_half_turn == self.turn
        ]

        for piece in passant_pieces:
            self.board.set(piece.position, None)


game = Game()

for half_turn in range(0, 50 * 2):
    game.next_turn()
