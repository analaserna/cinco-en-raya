"""Excepciones del juego cinco en raya."""


class InvalidMoveError(Exception):
    """Movimiento no permitido por las reglas del juego."""


class OutOfBoundsError(InvalidMoveError):
    """La casilla indicada está fuera del tablero."""


class OccupiedCellError(InvalidMoveError):
    """La casilla indicada ya está ocupada."""


class GameOverError(InvalidMoveError):
    """Se ha intentado jugar en una partida ya terminada."""