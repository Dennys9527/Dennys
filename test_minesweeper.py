import unittest
from minesweeper import Minesweeper


class MinesweeperTests(unittest.TestCase):
    def test_mine_counts(self) -> None:
        mines = {(0, 0), (1, 1)}
        game = Minesweeper(3, 3, len(mines), mine_positions=mines)
        self.assertEqual(game._board[0][0], -1)
        self.assertEqual(game._board[0][1], 2)
        self.assertEqual(game._board[2][2], 1)

    def test_reveal_expansion_and_win(self) -> None:
        mines = {(0, 0)}
        game = Minesweeper(3, 3, 1, mine_positions=mines)
        game.reveal(2, 2)
        self.assertTrue(game.is_win())
        self.assertEqual(len(game.revealed), 8)
        self.assertFalse(game.game_over)

    def test_reveal_mine(self) -> None:
        mines = {(1, 1)}
        game = Minesweeper(2, 2, 1, mine_positions=mines)
        safe = game.reveal(1, 1)
        self.assertFalse(safe)
        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()
