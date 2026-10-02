"""Lógica del juego cinco en raya."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from cincoenraya.errors import GameOverError, InvalidMoveError, OccupiedCellError, OutOfBoundsError

DEFAULT_SIZE = 15
WIN_LENGTH = 5
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


class Player(Enum):
    """Jugadores de la partida. BLACK mueve siempre en primer lugar."""

    BLACK = "X"
    WHITE = "O"

    def opponent(self) -> Player:
        """Devuelve el jugador contrario."""
        return Player.WHITE if self is Player.BLACK else Player.BLACK


@dataclass(frozen=True)
class Move:
    """Movimiento: colocar una ficha en la casilla (row, col)."""

    row: int
    col: int


class GameState:
    """Estado completo de una partida de cinco en raya."""

    def __init__(self, size: int = DEFAULT_SIZE) -> None:
        if size < WIN_LENGTH:
            raise ValueError(f"El tablero debe medir al menos {WIN_LENGTH}x{WIN_LENGTH}.")
        self.size = size
        self._board: list[list[Player | None]] = [[None] * size for _ in range(size)]
        self.current_player = Player.BLACK
        self.winner: Player | None = None
        self.move_count = 0
        self.last_move: Move | None = None

    def cell(self, row: int, col: int) -> Player | None:
        """Devuelve el jugador que ocupa la casilla, o None si está vacía."""
        return self._board[row][col]

    def in_bounds(self, move: Move) -> bool:
        """Indica si el movimiento cae dentro del tablero."""
        if not isinstance(move.row, int) or not isinstance(move.col, int):
            return False
        return 0 <= move.row < self.size and 0 <= move.col < self.size

    def is_full(self) -> bool:
        """Indica si no quedan casillas libres."""
        return self.move_count == self.size * self.size

    def is_over(self) -> bool:
        """Indica si la partida ha terminado por victoria o por empate."""
        return self.winner is not None or self.is_full()

    def is_legal(self, move: Move) -> bool:
        """Indica si el movimiento se puede jugar en el estado actual."""
        if self.is_over() or not self.in_bounds(move):
            return False
        return self._board[move.row][move.col] is None

    def legal_moves(self) -> list[Move]:
        """Devuelve todos los movimientos legales del estado actual."""
        if self.is_over():
            return []
        return [
            Move(row, col)
            for row in range(self.size)
            for col in range(self.size)
            if self._board[row][col] is None
        ]

    def play(self, move: Move) -> None:
        """Aplica el movimiento del jugador actual y pasa el turno.

        Si el movimiento completa una línea ganadora, la partida termina
        y el turno no cambia.

        Raises:
            InvalidMoveError: si el argumento no es un Move.
            GameOverError: si la partida ya ha terminado.
            OutOfBoundsError: si la casilla está fuera del tablero.
            OccupiedCellError: si la casilla ya está ocupada.
        """
        if not isinstance(move, Move):
            raise InvalidMoveError(f"Se esperaba un Move, se recibió {type(move).__name__}.")
        if self.is_over():
            raise GameOverError("La partida ya ha terminado.")
        if not self.in_bounds(move):
            raise OutOfBoundsError(f"La casilla ({move.row}, {move.col}) está fuera del tablero.")
        if self._board[move.row][move.col] is not None:
            raise OccupiedCellError(f"La casilla ({move.row}, {move.col}) ya está ocupada.")

        self._board[move.row][move.col] = self.current_player
        self.move_count += 1
        self.last_move = move

        if self._is_winning_move(move):
            self.winner = self.current_player
        else:
            self.current_player = self.current_player.opponent()

    def copy(self) -> GameState:
        """Devuelve una copia independiente del estado."""
        clone = GameState(self.size)
        clone._board = [row[:] for row in self._board]
        clone.current_player = self.current_player
        clone.winner = self.winner
        clone.move_count = self.move_count
        clone.last_move = self.last_move
        return clone

    def _count_direction(self, move: Move, d_row: int, d_col: int) -> int:
        """Cuenta fichas consecutivas del mismo jugador desde move en una dirección.

        No incluye la casilla de move.
        """
        player = self._board[move.row][move.col]
        count = 0
        row, col = move.row + d_row, move.col + d_col
        while 0 <= row < self.size and 0 <= col < self.size and self._board[row][col] is player:
            count += 1
            row += d_row
            col += d_col
        return count

    def _is_winning_move(self, move: Move) -> bool:
        """Indica si la ficha colocada en move forma una línea de WIN_LENGTH o más."""
        for d_row, d_col in DIRECTIONS:
            line = 1 + self._count_direction(move, d_row, d_col) + self._count_direction(move, -d_row, -d_col)
            if line >= WIN_LENGTH:
                return True
        return False

    def __str__(self) -> str:
        symbols = {None: ".", Player.BLACK: "X", Player.WHITE: "O"}
        return "\n".join(" ".join(symbols[cell] for cell in row) for row in self._board)