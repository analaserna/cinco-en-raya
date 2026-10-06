"""Detección de amenazas y búsqueda de victorias por cuatros continuos (VCF).

Un cuatro es una ventana con cuatro fichas de un jugador y una casilla
vacía: si el rival no la tapa, el jugador gana en su siguiente jugada.
Una victoria por cuatros continuos (VCF, victory by continuous fours) es
una secuencia de cuatros en la que el rival está obligado a tapar cada uno,
y que termina en una jugada que crea dos amenazas a la vez, imposibles de
tapar con una sola ficha.
"""

from __future__ import annotations

import time

from cincoenraya.bots.heuristics import nearby_moves, windows, windows_through
from cincoenraya.game import GameState, Move, Player


def threats_after(state: GameState, move: Move, player: Player) -> tuple[bool, set[tuple[int, int]]]:
    """Amenazas que consigue player al jugar en move, que debe estar vacía.

    Returns:
        Una pareja (gana, casillas). gana es True si la jugada forma cinco en
        línea. casillas son las casillas vacías con las que player formaría
        cinco en su siguiente jugada, es decir, los cuatros que crea.
    """
    wins = False
    cells: set[tuple[int, int]] = set()
    all_windows = windows(state.size)
    target = (move.row, move.col)
    for i in windows_through(state.size)[target]:
        mine = theirs = 0
        empty = []
        for cell in all_windows[i]:
            occupant = state.cell(*cell)
            if occupant is player:
                mine += 1
            elif occupant is None:
                if cell != target:
                    empty.append(cell)
            else:
                theirs += 1
        if theirs:
            continue
        if mine == 4:
            wins = True
        elif mine == 3:
            cells.update(empty)
    return wins, cells


def winning_cells(state: GameState, player: Player) -> set[tuple[int, int]]:
    """Casillas en las que player formaría cinco en línea en su siguiente jugada."""
    cells: set[tuple[int, int]] = set()
    for window in windows(state.size):
        mine = 0
        empty = None
        blocked = False
        for cell in window:
            occupant = state.cell(*cell)
            if occupant is player:
                mine += 1
            elif occupant is None:
                empty = cell
            else:
                blocked = True
                break
        if not blocked and mine == 4 and empty is not None:
            cells.add(empty)
    return cells


def with_turn_passed(state: GameState) -> GameState:
    """Copia del estado en la que le toca mover al otro jugador, como si se pasara el turno."""
    passed = state.copy()
    passed.current_player = state.current_player.opponent()
    return passed


def find_vcf(state: GameState, depth: int = 10, deadline: float | None = None) -> Move | None:
    """Busca una victoria por cuatros continuos para el jugador al que le toca.

    Args:
        state: posición de partida.
        depth: número máximo de cuatros consecutivos del atacante.
        deadline: instante, medido con time.perf_counter, a partir del cual
            se abandona la búsqueda.

    Returns:
        La primera jugada de una victoria por cuatros continuos, o None si no
        la encuentra en la profundidad o el tiempo disponibles.
    """
    if depth <= 0 or (deadline is not None and time.perf_counter() > deadline):
        return None

    attacker = state.current_player
    defender = attacker.opponent()

    fours = []
    for move in nearby_moves(state, distance=2):
        wins, cells = threats_after(state, move, attacker)
        if wins:
            return move
        if cells:
            fours.append((move, cells))

    if winning_cells(state, defender):
        return None

    for move, cells in fours:
        if len(cells) >= 2:
            return move
        block = Move(*next(iter(cells)))
        child = state.copy()
        child.play(move)
        counter_win, counter_cells = threats_after(child, block, defender)
        if counter_win or counter_cells:
            continue
        child.play(block)
        if find_vcf(child, depth - 1, deadline) is not None:
            return move
    return None