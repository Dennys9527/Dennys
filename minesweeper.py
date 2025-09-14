import random
from dataclasses import dataclass
from typing import List, Set, Tuple, Optional


Coordinate = Tuple[int, int]


@dataclass
class Minesweeper:
    """Simple terminal-based Minesweeper game."""

    rows: int
    cols: int
    mines_count: int
    mine_positions: Optional[Set[Coordinate]] = None
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("Board dimensions must be positive")
        if self.mines_count >= self.rows * self.cols:
            raise ValueError("Too many mines for the board size")

        if self.mine_positions is not None:
            if len(self.mine_positions) != self.mines_count:
                raise ValueError("mine_positions length must equal mines_count")
            self.mines = set(self.mine_positions)
        else:
            rng = random.Random(self.seed)
            all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
            self.mines = set(rng.sample(all_cells, self.mines_count))

        self._board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for r, c in self.mines:
            self._board[r][c] = -1
        for r in range(self.rows):
            for c in range(self.cols):
                if self._board[r][c] == -1:
                    continue
                self._board[r][c] = self._adjacent_mines(r, c)

        self.revealed: Set[Coordinate] = set()
        self.flags: Set[Coordinate] = set()
        self.game_over = False

    def _adjacent_cells(self, r: int, c: int) -> List[Coordinate]:
        cells: List[Coordinate] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    cells.append((nr, nc))
        return cells

    def _adjacent_mines(self, r: int, c: int) -> int:
        return sum((nr, nc) in self.mines for nr, nc in self._adjacent_cells(r, c))

    def reveal(self, r: int, c: int) -> bool:
        if self.game_over:
            return False
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError("Cell out of range")
        if (r, c) in self.revealed or (r, c) in self.flags:
            return True

        self.revealed.add((r, c))
        if (r, c) in self.mines:
            self.game_over = True
            return False

        if self._board[r][c] == 0:
            for nr, nc in self._adjacent_cells(r, c):
                if (nr, nc) not in self.revealed:
                    self.reveal(nr, nc)
        return True

    def flag(self, r: int, c: int) -> None:
        if self.game_over:
            return
        if (r, c) in self.revealed:
            return
        if (r, c) in self.flags:
            self.flags.remove((r, c))
        else:
            self.flags.add((r, c))

    def is_win(self) -> bool:
        return len(self.revealed) == self.rows * self.cols - self.mines_count

    def board_str(self, reveal_all: bool = False) -> str:
        lines: List[str] = []
        for r in range(self.rows):
            cells: List[str] = []
            for c in range(self.cols):
                pos = (r, c)
                if reveal_all or pos in self.revealed:
                    if pos in self.mines:
                        cells.append("*")
                    else:
                        val = self._board[r][c]
                        cells.append(" " if val == 0 else str(val))
                elif pos in self.flags:
                    cells.append("F")
                else:
                    cells.append("#")
            lines.append(" ".join(cells))
        return "\n".join(lines)


def play() -> None:
    print("Minesweeper! Enter moves as 'r c' to reveal or 'f r c' to flag.")
    try:
        rows = int(input("Rows (default 9): ") or 9)
        cols = int(input("Cols (default 9): ") or 9)
        mines = int(input("Mines (default 10): ") or 10)
    except ValueError:
        print("Invalid input, using defaults 9x9 with 10 mines.")
        rows, cols, mines = 9, 9, 10

    game = Minesweeper(rows, cols, mines)
    while not game.game_over and not game.is_win():
        print(game.board_str())
        move = input("Move: ").strip().split()
        if not move:
            continue
        try:
            if move[0].lower() == "f" and len(move) == 3:
                r, c = int(move[1]), int(move[2])
                game.flag(r, c)
            elif len(move) == 2:
                r, c = int(move[0]), int(move[1])
                safe = game.reveal(r, c)
                if not safe:
                    print("Boom! You hit a mine.")
            else:
                print("Invalid move format.")
        except ValueError:
            print("Invalid coordinates.")

    print(game.board_str(reveal_all=True))
    if game.is_win():
        print("Congratulations, you win!")
    else:
        print("Game over.")


if __name__ == "__main__":
    play()
