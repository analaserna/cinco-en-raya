"""Cinco en raya: juego por turnos para dos jugadores con soporte para bots."""

from cincoenraya.errors import GameOverError, InvalidMoveError, OccupiedCellError, OutOfBoundsError
from cincoenraya.game import GameState, Move, Player

__version__ = "0.1.0"

__all__ = [
    "GameOverError",
    "GameState",
    "InvalidMoveError",
    "Move",
    "OccupiedCellError",
    "OutOfBoundsError",
    "Player",
]