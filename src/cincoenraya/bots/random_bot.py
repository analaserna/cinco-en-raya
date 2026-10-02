"""Bot que juega movimientos legales al azar."""

from __future__ import annotations

import random

from cincoenraya.bot import Bot
from cincoenraya.game import GameState, Move


class RandomBot(Bot):
    """Elige un movimiento legal al azar.

    Sirve como rival de referencia y para probar la plataforma.

    Args:
        seed: semilla opcional para que las partidas sean reproducibles.
    """

    name = "Aleatorio"

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_move(self, state: GameState) -> Move:
        return self._rng.choice(state.legal_moves())