"""API pública para implementar bots de cinco en raya."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cincoenraya.game import GameState, Move


class Bot(ABC):
    """Clase base que deben heredar todos los bots.

    Para crear un bot basta con heredar de esta clase e implementar
    choose_move. No es necesario modificar el código del juego.

    Attributes:
        name: nombre del bot que se muestra en la interfaz y en la clasificación.
    """

    name: str = "Bot sin nombre"

    @abstractmethod
    def choose_move(self, state: GameState) -> Move:
        """Elige el siguiente movimiento.

        Args:
            state: copia del estado actual de la partida. El bot juega con las
                fichas de state.current_player. Puede modificar esta copia
                libremente sin afectar a la partida real.

        Returns:
            El movimiento elegido. Debe ser legal en el estado recibido;
            un movimiento ilegal hace perder la partida.
        """

    def __str__(self) -> str:
        return self.name