"""Bot que elige la jugada que más mejora la evaluación por ventanas."""

from __future__ import annotations

import random

from cincoenraya.bot import Bot
from cincoenraya.bots.heuristics import makes_five, move_delta, nearby_moves
from cincoenraya.game import GameState, Move


class PatternBot(Bot):
    """Bot que mira una sola jugada usando la evaluación por ventanas.

    Por orden de prioridad:
        1. Si puede formar cinco en línea, lo hace.
        2. Si el rival puede formar cinco en línea, le bloquea.
        3. Si no, elige la casilla cercana que más aumenta la evaluación
           (move_delta). Este valor tiene en cuenta a la vez el ataque propio
           y la defensa, porque poner una ficha en una ventana del rival
           anula el valor que tenía para él.

    Args:
        seed: semilla opcional para desempatar entre casillas igual de buenas.
    """

    name = "Patrones"

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_move(self, state: GameState) -> Move:
        me = state.current_player
        rival = me.opponent()
        candidates = nearby_moves(state)

        for move in candidates:
            if makes_five(state, move, me):
                return move
        for move in candidates:
            if makes_five(state, move, rival):
                return move

        scores = {move: move_delta(state, move, me) for move in candidates}
        best = max(scores.values())
        return self._rng.choice([move for move, score in scores.items() if score == best])