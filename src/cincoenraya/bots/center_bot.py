"""Bot de ejemplo: juega en la casilla libre más cercana al centro."""

from cincoenraya.bot import Bot
from cincoenraya.game import GameState, Move


class CenterBot(Bot):
    """Elige la casilla libre más próxima al centro del tablero."""

    name = "Centro"

    def choose_move(self, state: GameState) -> Move:
        center = (state.size - 1) / 2
        return min(
            state.legal_moves(),
            key=lambda move: (move.row - center) ** 2 + (move.col - center) ** 2,
        )