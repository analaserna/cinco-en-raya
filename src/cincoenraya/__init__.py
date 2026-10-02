"""Cinco en raya: juego por turnos para dos jugadores con soporte para bots."""

from cincoenraya.bot import Bot
from cincoenraya.errors import GameOverError, InvalidMoveError, OccupiedCellError, OutOfBoundsError
from cincoenraya.game import GameState, Move, Player
from cincoenraya.match import EndReason, MatchResult, play_match

__version__ = "0.1.0"

__all__ = [
    "Bot",
    "EndReason",
    "GameOverError",
    "GameState",
    "InvalidMoveError",
    "MatchResult",
    "Move",
    "OccupiedCellError",
    "OutOfBoundsError",
    "Player",
    "play_match",
]