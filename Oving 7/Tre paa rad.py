from math import ceil, floor
from re import sub

FlatMatrix = list[str | None]
Matrix = list[FlatMatrix]

NUMBER_OF_PLAYERS = 3
WINNER_LENGTH = 2
BOARD_HEIGHT = 3
BOARD_WIDTH = 5


class StopExecution(Exception):
    def _render_traceback_(self):
        return []


def clean_exit() -> None:
    raise StopExecution


def handle_input(raw_input_string: str) -> str:
    if raw_input_string.lower() in ["quit", "exit", "\q"]:
        clean_exit()

    return raw_input_string


def to_str_or_none(input: any) -> str | None:
    if input is None:
        return None

    return str(input)


# utgangspunkt fra `Matriseaddisjon.ipynb`
def create_matrix(height: int, width: int, data: FlatMatrix) -> Matrix:
    return [
        [to_str_or_none(data[x + width * y]) for x in range(width)]
        for y in range(height)
    ]


# fra `Matriseaddisjon.ipynb`
def flatten_matrix(data: Matrix) -> FlatMatrix:
    return [x for y in data for x in y]


def pad(string: str, left: int = 1, right: int = 1) -> str:
    return (" " * left) + string + (" " * right)


def center_string(string: str, width: int) -> str:
    difference = width - len(string)
    padding_smaller = difference // 2
    padding_bigger = difference - padding_smaller

    return pad(string, padding_smaller, padding_bigger)


def pad_cells(matrix: Matrix) -> Matrix:
    matrix_height = len(matrix)
    matrix_width = len(matrix[0])
    max_widths = []

    for x in range(len(matrix[0])):
        column_max_width = 0

        for y in range(len(matrix)):
            if matrix[y][x] is None:
                continue

            if len(matrix[y][x]) > column_max_width:
                column_max_width = len(matrix[y][x])

        max_widths.append(column_max_width)

    flat_matrix = flatten_matrix(matrix)
    cells = []

    for i in range(0, len(flat_matrix)):
        x = i % matrix_width

        to_append = " " if flat_matrix[i] is None else flat_matrix[i]
        to_append = pad(to_append.ljust(max_widths[x], " "))

        cells.append(to_append)

    return create_matrix(matrix_height, matrix_width, cells)


def get_prefix(height) -> list[str]:
    upper_bound_plus_one = len(str(height))
    spacer = pad(" ", upper_bound_plus_one - 1, 1)

    prefix = [spacer, spacer]

    for i in range(1, height + 1):
        prefix.append(pad(str(i), upper_bound_plus_one - len(str(i)), 1))
        prefix.append(spacer)

    return prefix


def get_row_separator(first_row_of_cells: FlatMatrix) -> str:
    row_separator = "+"

    for cell in first_row_of_cells:
        row_separator += "-" * len(cell) + "+"

    return row_separator


def print_header(matrix_width: int, first_row_of_cells: FlatMatrix) -> None:
    for column in range(0, matrix_width):
        column_width = len(first_row_of_cells[column])
        string = str(column + 1)

        print(" " + center_string(string, column_width), end="")

    print("")


def print_matrix(matrix: Matrix) -> None:
    matrix_height = len(matrix)
    matrix_width = len(matrix[0])

    prefix = get_prefix(matrix_height)
    cells = pad_cells(matrix)

    row_separator = get_row_separator(cells[0])

    for i in range(0, matrix_height * 2 + 2):
        print(prefix[i], end="")

        if i == 0:
            print_header(matrix_width, cells[0])
            continue

        if i % 2 != 0:
            print(row_separator)
            continue

        print("|", end="")

        cell_index = ceil((i - 2) / 2)

        for cell in cells[cell_index][:-1]:
            print(f"{cell}|", end="")

        print(f"{cells[cell_index][-1]}|")


def all_equal(list: list) -> bool:
    return len(set(list)) == 1 and list[0] is not None


def get_winner(matrix: Matrix) -> str | bool | None:
    """
    str   => aliaset til vinneren
    False => spillet er ikke ferdig
    None  => spillet er uavgjort
    """

    matrix_height = len(matrix)
    matrix_width = len(matrix[0])

    if matrix_height != BOARD_HEIGHT or matrix_width != BOARD_WIDTH:
        raise ValueError(f"Matrix is not {BOARD_WIDTH}x{BOARD_HEIGHT}")

    has_none = False
    shift = WINNER_LENGTH - 1

    # _ _ _
    # X X X
    # _ _ _
    for y in range(0, matrix_height):
        if None in matrix[y]:
            has_none = True

        for x in range(0, matrix_width - shift):
            if matrix[y][x] == None:
                continue

            if all_equal([matrix[y][x + i] for i in range(0, WINNER_LENGTH)]):
                return matrix[y][x]

    if not has_none:
        return False

    # _ X _
    # _ X _
    # _ X _
    for x in range(0, matrix_width):
        for y in range(0, matrix_height - shift):
            if matrix[y][x] == None:
                continue

            if all_equal([matrix[y + i][x] for i in range(0, WINNER_LENGTH)]):
                return matrix[y][x]

    # X _ _
    # _ X _
    # _ _ X
    for y in range(0, matrix_height - shift):
        for x in range(0, matrix_width - shift):
            if matrix[y][x] == None:
                continue

            if all_equal([matrix[y + i][x + i] for i in range(0, WINNER_LENGTH)]):
                return matrix[y][x]

    # _ _ X
    # _ X _
    # X _ _
    for y in range(0, matrix_height - shift):
        for x in range(shift, matrix_width):
            if matrix[y][x] == None:
                continue

            if all_equal([matrix[y + i][x - i] for i in range(0, WINNER_LENGTH)]):
                return matrix[y][x]

    return None


def assign_players(number_of_players: int) -> dict[str, str]:
    players: dict[str, str] = {}

    while len(players) < NUMBER_OF_PLAYERS:
        n = len(players) + 1

        name = handle_input(input(f"Spiller {n}: "))

        if name in players.keys():
            print(f"Navnet '{name}' er allerede tatt. Prøv på nytt.")
            continue

        alias = handle_input(input(f"Alias for {name} (spiller {n}): "))

        if alias in players.values():
            print(f"Aliaset '{alias}' er allerede tatt. Prøv på nytt.")
            continue

        players.update({name: alias})

    return players


def is_legal_move(board: Matrix, to_coordinate: (int, int)) -> bool:
    x, y = to_coordinate

    if board[y - 1][x - 1] is not None:
        return False

    return True


def validate_coordinate_input(matrix: Matrix, coordinate: (int, int)) -> bool:
    if len(coordinate) != 2:
        return False

    x, y = coordinate

    if not isinstance(x, int) or not isinstance(y, int):
        return False

    matrix_height = len(matrix)
    matrix_width = len(matrix[0])

    if 1 <= x <= matrix_width and 1 <= y <= matrix_height:
        return True

    return False


def get_next_coordinate(board: Matrix) -> (int, int):
    coordinate = None

    while coordinate == None:
        raw_coordinate = handle_input(input("Velg koordinat (x, y): "))
        cleaned_coordinate = sub(r"[^0-9,]", "", raw_coordinate)
        x_y_split = cleaned_coordinate.split(",")

        if len(x_y_split) != 2:
            print(f"Ugyldig koordinat {raw_coordinate}. Prøv igjen.")
            continue

        try:
            x = int(x_y_split[0])
            y = int(x_y_split[1])

            if not validate_coordinate_input(board, (x, y)):
                print(f"Ugyldig koordinat {raw_coordinate}. Prøv igjen.")
                continue

            if not is_legal_move(board, (x, y)):
                print(f"Ugyldig trekk {raw_coordinate}. Prøv igjen.")
                continue

            coordinate = (x, y)
        except:
            print(f"Ugyldig koordinat {raw_coordinate}. Prøv igjen.")
            continue

    return coordinate


empty_data = [None for _ in range(0, BOARD_HEIGHT * BOARD_WIDTH)]
board = create_matrix(BOARD_HEIGHT, BOARD_WIDTH, empty_data)

winner = get_winner(board)
players = assign_players(2)

i = 0
while winner == None:
    i += 1

    for name, alias in players.items():
        print("\n\n")
        print_matrix(board)
        print(f"Runde {i} - {WINNER_LENGTH} på rad - {len(players)} spillere\n")
        print(f"Spiller {name} ({alias}) sin tur")

        x, y = get_next_coordinate(board)

        board[y - 1][x - 1] = alias

        winner = get_winner(board)

        if winner != None:
            break

if winner == False:
    print("\n\n")
    print_matrix(board)
    print("\nSpillet er ferdig. Det ble uavgjort.")

winner_name = list(players.keys())[list(players.values()).index(winner)]

print("\n\n")
print_matrix(board)
print(f"\nSpillet er ferdig. Spiller {winner_name} ({winner}) vant!")
