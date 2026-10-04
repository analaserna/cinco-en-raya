"""Bot táctico: gana si puede, bloquea si debe y si no, alarga sus líneas."""

from __future__ import annotations

import random

from cincoenraya.bot import Bot
from cincoenraya.game import DIRECTIONS, WIN_LENGTH, GameState, Move, Player


class GreedyBot(Bot):
    """Bot que decide mirando solo el movimiento actual.

    Por orden de prioridad:
        1. Si puede formar cinco en línea, lo hace.
        2. Si el rival puede formar cinco en línea, le bloquea.
        3. Si no, elige la casilla que más alarga sus líneas o más corta
           las del rival, entre las casillas cercanas a fichas existentes.

    Args:
        seed: semilla opcional para desempatar entre casillas igual de buenas.
    """

    name = "Táctico"

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_move(self, state: GameState) -> Move:
        me = state.current_player
        rival = me.opponent()
        candidates = self._candidates(state)

        for move in candidates:
            if self._line_length(state, move, me) >= WIN_LENGTH:
                return move

        for move in candidates:
            if self._line_length(state, move, rival) >= WIN_LENGTH:
                return move

        scores = {move: self._score(state, move, me, rival) for move in candidates}
        best = max(scores.values())
        return self._rng.choice([move for move, score in scores.items() if score == best])

    def _candidates(self, state: GameState) -> list[Move]:
        """Casillas vacías a distancia 1 de alguna ficha, o el centro si el tablero está vacío."""
        if state.move_count == 0:
            center = state.size // 2
            return [Move(center, center)]

        candidates = []
        for move in state.legal_moves():
            for d_row in (-1, 0, 1):
                for d_col in (-1, 0, 1):
                    row, col = move.row + d_row, move.col + d_col
                    if 0 <= row < state.size and 0 <= col < state.size and state.cell(row, col) is not None:
                        candidates.append(move)
                        break
                else:
                    continue
                break
        return candidates or state.legal_moves()

    @staticmethod
    def _line_length(state: GameState, move: Move, player: Player) -> int:
        """Longitud de la línea más larga que formaría player al jugar en move."""
        best = 0
        for d_row, d_col in DIRECTIONS:
            length = 1
            for sign in (1, -1):
                row, col = move.row + sign * d_row, move.col + sign * d_col
                while 0 <= row < state.size and 0 <= col < state.size and state.cell(row, col) is player:
                    length += 1
                    row += sign * d_row
                    col += sign * d_col
            best = max(best, length)
        return best

    def _score(self, state: GameState, move: Move, me: Player, rival: Player) -> int:
        """Valora una casilla: atacar pesa el doble que defender."""
        attack = self._line_length(state, move, me)
        defense = self._line_length(state, move, rival)
        return 2 * attack**2 + defense**2