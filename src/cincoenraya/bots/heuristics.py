"""Evaluación heurística de posiciones de cinco en raya basada en ventanas.

Una ventana es un grupo de WIN_LENGTH casillas consecutivas en horizontal,
vertical o diagonal. Cada ventana que solo contiene fichas de un jugador es
una posible línea ganadora para él, y vale más cuantas más fichas tenga.
Las ventanas con fichas de ambos jugadores ya no pueden dar la victoria a
nadie y valen 0.
"""

from __future__ import annotations

from functools import lru_cache

from cincoenraya.game import DIRECTIONS, WIN_LENGTH, GameState, Move, Player

WIN_SCORE = 10_000_000
WINDOW_SCORES = (0, 1, 10, 100, 10_000)

Cell = tuple[int, int]


@lru_cache(maxsize=None)
def windows(size: int) -> tuple[tuple[Cell, ...], ...]:
    """Todas las ventanas de WIN_LENGTH casillas consecutivas de un tablero."""
    result = []
    for row in range(size):
        for col in range(size):
            for d_row, d_col in DIRECTIONS:
                end_row = row + d_row * (WIN_LENGTH - 1)
                end_col = col + d_col * (WIN_LENGTH - 1)
                if 0 <= end_row < size and 0 <= end_col < size:
                    result.append(tuple((row + d_row * k, col + d_col * k) for k in range(WIN_LENGTH)))
    return tuple(result)


@lru_cache(maxsize=None)
def windows_through(size: int) -> dict[Cell, tuple[int, ...]]:
    """Para cada casilla, los índices de las ventanas que la contienen."""
    index: dict[Cell, list[int]] = {}
    for i, window in enumerate(windows(size)):
        for cell in window:
            index.setdefault(cell, []).append(i)
    return {cell: tuple(ids) for cell, ids in index.items()}


def window_score(mine: int, theirs: int) -> int:
    """Valor de una ventana con mine fichas propias y theirs fichas rivales."""
    if mine and theirs:
        return 0
    if mine:
        return WIN_SCORE if mine >= WIN_LENGTH else WINDOW_SCORES[mine]
    if theirs:
        return -(WIN_SCORE if theirs >= WIN_LENGTH else WINDOW_SCORES[theirs])
    return 0


def _count(state: GameState, window: tuple[Cell, ...], player: Player) -> tuple[int, int]:
    """Cuenta las fichas de player y de su rival en una ventana."""
    mine = theirs = 0
    for row, col in window:
        occupant = state.cell(row, col)
        if occupant is player:
            mine += 1
        elif occupant is not None:
            theirs += 1
    return mine, theirs


def evaluate(state: GameState, player: Player) -> int:
    """Valoración de la posición para player: positiva si le favorece."""
    if state.winner is not None:
        return WIN_SCORE if state.winner is player else -WIN_SCORE
    return sum(window_score(*_count(state, window, player)) for window in windows(state.size))


def move_delta(state: GameState, move: Move, player: Player) -> int:
    """Cambio de evaluate(state, player) si el jugador al que le toca juega en move.

    Solo recorre las ventanas que contienen la casilla del movimiento, por lo
    que es mucho más rápido que evaluar el tablero entero antes y después.
    La casilla debe estar vacía.
    """
    mover = state.current_player
    all_windows = windows(state.size)
    delta = 0
    for i in windows_through(state.size)[(move.row, move.col)]:
        mine, theirs = _count(state, all_windows[i], player)
        before = window_score(mine, theirs)
        if mover is player:
            mine += 1
        else:
            theirs += 1
        delta += window_score(mine, theirs) - before
    return delta


def nearby_moves(state: GameState, distance: int = 1) -> list[Move]:
    """Casillas vacías a una distancia máxima de alguna ficha.

    Si el tablero está vacío, devuelve solo el centro.
    """
    if state.move_count == 0:
        center = state.size // 2
        return [Move(center, center)]
    found = set()
    for row in range(state.size):
        for col in range(state.size):
            if state.cell(row, col) is None:
                continue
            for d_row in range(-distance, distance + 1):
                for d_col in range(-distance, distance + 1):
                    r, c = row + d_row, col + d_col
                    if 0 <= r < state.size and 0 <= c < state.size and state.cell(r, c) is None:
                        found.add((r, c))
    return [Move(r, c) for r, c in sorted(found)] or state.legal_moves()


def makes_five(state: GameState, move: Move, player: Player) -> bool:
    """Indica si player formaría una línea ganadora al jugar en move."""
    for d_row, d_col in DIRECTIONS:
        length = 1
        for sign in (1, -1):
            r, c = move.row + sign * d_row, move.col + sign * d_col
            while 0 <= r < state.size and 0 <= c < state.size and state.cell(r, c) is player:
                length += 1
                r += sign * d_row
                c += sign * d_col
        if length >= WIN_LENGTH:
            return True
    return False