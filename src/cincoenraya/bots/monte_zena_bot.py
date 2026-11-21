"""Bot monte_zena: negamax con poda alfa-beta y tabla de transposición.

El cinco en raya es un juego de dos jugadores, de suma cero y con
información perfecta: lo que gana un jugador lo pierde el otro y ambos ven
todo el tablero. Por eso el minimax se puede escribir en su forma negamax,
en la que el valor de una posición para un jugador es el opuesto de su
valor para el rival:

    valor(posición, yo) = max(-valor(hija, rival) para cada jugada)

Así basta una sola función en lugar de alternar entre maximizar y minimizar.
"""

from __future__ import annotations

import math
import random
import time
from functools import lru_cache

from cincoenraya.bot import Bot
from cincoenraya.bots.heuristics import WINDOW_SCORES, windows, windows_through
from cincoenraya.bots.threats import find_vcf, with_turn_passed
from cincoenraya.game import GameState, Move, Player

MATE = 1_000_000_000
"""Valor de una victoria. Es mayor que cualquier evaluación heurística."""

_MATE_BOUND = MATE - 10_000
_EXACT, _LOWER, _UPPER = 0, 1, 2
_SC = WINDOW_SCORES
_EMPTY, _BLACK, _WHITE = 0, 1, 2
_MAX_TT_ENTRIES = 1_000_000


class _Timeout(Exception):
    """Se ha agotado el tiempo de búsqueda."""


@lru_cache(maxsize=None)
def _tables(size: int) -> tuple:
    """Tablas precalculadas para un tamaño de tablero.

    Las casillas se numeran como row * size + col.

    Returns:
        (through, neighbors, zobrist): las ventanas que pasan por cada
        casilla, las casillas vecinas de cada casilla y las claves Zobrist
        aleatorias de cada casilla para cada color.
    """
    through_map = windows_through(size)
    through = tuple(through_map.get((i // size, i % size), ()) for i in range(size * size))
    neighbors = tuple(
        tuple(
            r * size + c
            for r in range(i // size - 1, i // size + 2)
            for c in range(i % size - 1, i % size + 2)
            if 0 <= r < size and 0 <= c < size and (r, c) != (i // size, i % size)
        )
        for i in range(size * size)
    )
    rng = random.Random(size)
    zobrist = tuple((0, rng.getrandbits(64), rng.getrandbits(64)) for _ in range(size * size))
    return through, neighbors, zobrist


class MonteZenaBot(Bot):
    """Bot que busca con negamax y poda alfa-beta.

    Antes de la búsqueda comprueba las victorias forzadas: si tiene una
    victoria por cuatros continuos (VCF), la juega; si la tendría el rival,
    solo considera las jugadas que la impiden.

    Después hace una búsqueda con profundidad iterativa (1, 2,
    3... jugadas) hasta max_depth o hasta agotar time_limit, y juega la mejor
    jugada de la última búsqueda completa. Para que la poda sea eficaz:

    - Tabla de transposición: guarda el valor y la mejor jugada de cada
      posición ya analizada, identificada por su hash Zobrist. Si se llega
      a la misma posición por otro orden de jugadas, no se vuelve a buscar.
      Se conserva entre movimientos.
    - Ordenación de jugadas: primero la mejor jugada según la tabla, después
      las jugadas killer (las que provocaron una poda a la misma
      profundidad) y después el resto por mejora de la evaluación.
    - Jugadas forzadas: si el jugador puede hacer cinco, la posición está
      ganada sin buscar más; si el rival tiene un cuatro, solo se exploran
      las casillas que lo tapan.
    - Tablero propio con hacer/deshacer jugada, en lugar de copiar el estado,
      y evaluación por ventanas actualizada de forma incremental.

    Args:
        max_depth: profundidad máxima de búsqueda.
        time_limit: segundos de cálculo por movimiento.
        max_branching: número máximo de jugadas que explora en cada posición.

    Attributes:
        last_depth: profundidad de la última búsqueda completa en el último
            movimiento, o 0 si no hizo falta buscar.
        last_nodes: posiciones visitadas en el último movimiento.
    """

    name = "monte_zena"

    def __init__(self, max_depth: int = 12, time_limit: float = 0.4, max_branching: int = 8) -> None:
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.max_branching = max_branching
        self.last_depth = 0
        self.last_nodes = 0
        self._tt: dict[int, tuple[int, int, int, int]] = {}
        self._tt_board_size = 0
        self._deadline = math.inf

    # ------------------------------------------------------------------
    # Movimiento
    # ------------------------------------------------------------------

    def choose_move(self, state: GameState) -> Move:
        self.last_depth = 0
        self.last_nodes = 0
        size = state.size
        if state.move_count == 0:
            return Move(size // 2, size // 2)

        self._setup(state)
        me = _BLACK if state.current_player is Player.BLACK else _WHITE
        win, moves = self._generate(me)
        if win is not None:
            return self._to_move(win)
        if not moves:
            return state.legal_moves()[0]
        if len(moves) == 1:
            return self._to_move(moves[0][1])

        start = time.perf_counter()
        winning = find_vcf(state, deadline=start + 0.2 * self.time_limit)
        if winning is not None:
            return winning
        moves = self._vcf_defenses(state, moves, start + 0.5 * self.time_limit)

        self._deadline = start + self.time_limit
        best = moves[0][1]
        for depth in range(1, self.max_depth + 1):
            try:
                best, value = self._root(depth, me, moves, best)
            except _Timeout:
                break
            self.last_depth = depth
            if abs(value) >= _MATE_BOUND:
                break
        return self._to_move(best)

    def _to_move(self, index: int) -> Move:
        return Move(index // self._size, index % self._size)

    def _vcf_defenses(
        self, state: GameState, moves: list[tuple[int, int]], deadline: float
    ) -> list[tuple[int, int]]:
        """Restringe las jugadas a las que impiden una victoria forzada del rival.

        Imagina que pasa el turno y busca si el rival tendría una victoria
        por cuatros continuos (VCF). Si no la tiene, devuelve moves sin
        cambios. Si la tiene, devuelve solo las jugadas tras las cuales el
        rival deja de tenerla, o moves sin cambios si ninguna lo consigue.
        """
        threat = find_vcf(with_turn_passed(state), deadline=deadline)
        if threat is None:
            return moves

        gains = {i: gain for gain, i in moves}
        threat_cell = threat.row * self._size + threat.col
        options = [threat_cell] + [i for _, i in moves[: 2 * self.max_branching] if i != threat_cell]
        safe = []
        for i in options:
            if time.perf_counter() > deadline:
                break
            child = state.copy()
            child.play(self._to_move(i))
            if find_vcf(child, deadline=deadline) is None:
                safe.append((gains.get(i, 0), i))
        if not safe:
            return moves
        safe.sort(reverse=True)
        return safe

    # ------------------------------------------------------------------
    # Tablero interno
    # ------------------------------------------------------------------

    def _setup(self, state: GameState) -> None:
        """Copia el estado a las estructuras internas de la búsqueda."""
        size = state.size
        self._size = size
        self._n = size * size
        self._through, self._neighbors, self._zobrist = _tables(size)
        n_windows = len(windows(size))
        self._board = [_EMPTY] * self._n
        self._counts = (None, [0] * n_windows, [0] * n_windows)
        self._near = [0] * self._n
        self._score = 0
        self._hash = 0
        self._nodes = 0
        self._killers: dict[int, list[int]] = {}

        if self._tt_board_size != size or len(self._tt) > _MAX_TT_ENTRIES:
            self._tt = {}
            self._tt_board_size = size

        for row in range(size):
            for col in range(size):
                occupant = state.cell(row, col)
                if occupant is not None:
                    self._play(row * size + col, _BLACK if occupant is Player.BLACK else _WHITE)

    def _play(self, i: int, p: int) -> int:
        """Coloca una ficha de p en la casilla i y devuelve el cambio de evaluación para p."""
        self._board[i] = p
        mine, theirs = self._counts[p], self._counts[3 - p]
        delta = 0
        for w in self._through[i]:
            m, t = mine[w], theirs[w]
            if t == 0:
                delta += _SC[m + 1] - _SC[m] if m < 4 else 0
            elif m == 0:
                delta += _SC[t]
            mine[w] = m + 1
        self._score += delta if p == _BLACK else -delta
        near = self._near
        for j in self._neighbors[i]:
            near[j] += 1
        self._hash ^= self._zobrist[i][p]
        return delta

    def _undo(self, i: int, p: int, delta: int) -> None:
        """Deshace _play(i, p)."""
        self._board[i] = _EMPTY
        mine = self._counts[p]
        for w in self._through[i]:
            mine[w] -= 1
        self._score -= delta if p == _BLACK else -delta
        near = self._near
        for j in self._neighbors[i]:
            near[j] -= 1
        self._hash ^= self._zobrist[i][p]

    def _generate(self, p: int) -> tuple[int | None, list[tuple[int, int]]]:
        """Jugadas candidatas para p: casillas vacías junto a alguna ficha.

        Returns:
            (victoria, jugadas). Si p puede formar cinco, victoria es esa
            casilla y jugadas está vacía. Si no, victoria es None y jugadas
            es una lista de parejas (ganancia, casilla) ordenada de mayor a
            menor ganancia. Si el rival tiene algún cuatro, solo se incluyen
            las casillas que lo tapan.
        """
        board, near = self._board, self._near
        mine, theirs = self._counts[p], self._counts[3 - p]
        through = self._through
        scored = []
        blocks = []
        for i in range(self._n):
            if board[i] or not near[i]:
                continue
            gain = 0
            block = False
            for w in through[i]:
                m, t = mine[w], theirs[w]
                if t == 0:
                    if m == 4:
                        return i, []
                    gain += _SC[m + 1] - _SC[m]
                elif m == 0:
                    if t == 4:
                        block = True
                    gain += _SC[t]
            scored.append((gain, i))
            if block:
                blocks.append((gain, i))
        result = blocks or scored
        result.sort(reverse=True)
        return None, result

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------

    def _order(self, moves: list[tuple[int, int]], first: int | None, ply: int) -> list[int]:
        """Orden en que se exploran las jugadas de una posición."""
        if len(moves) <= self.max_branching:
            cells = [i for _, i in moves]
        else:
            cells = [i for _, i in moves[: self.max_branching]]
        allowed = {i for _, i in moves}
        front = []
        for i in (first, *self._killers.get(ply, ())):
            if i is not None and i in allowed and i not in front:
                front.append(i)
        return front + [i for i in cells if i not in front]

    def _root(self, depth: int, p: int, moves: list[tuple[int, int]], first: int) -> tuple[int, int]:
        """Mejor jugada y su valor con una búsqueda a la profundidad indicada."""
        alpha, beta = -math.inf, math.inf
        best_move, best_value = first, -math.inf
        for i in self._order(moves, first, 0):
            delta = self._play(i, p)
            value = -self._negamax(depth - 1, -beta, -alpha, 3 - p, 1)
            self._undo(i, p, delta)
            if value > best_value:
                best_move, best_value = i, value
            alpha = max(alpha, value)
        return best_move, best_value

    def _negamax(self, depth: int, alpha: float, beta: float, p: int, ply: int) -> float:
        """Valor de la posición actual para p, el jugador al que le toca."""
        self._nodes += 1
        self.last_nodes = self._nodes
        if not self._nodes & 511 and time.perf_counter() > self._deadline:
            raise _Timeout

        win, moves = self._generate(p)
        if win is not None:
            return MATE - ply
        if not moves:
            return 0
        if depth <= 0:
            return self._score if p == _BLACK else -self._score

        key = self._hash
        original_alpha = alpha
        tt_move = None
        entry = self._tt.get(key)
        if entry is not None:
            entry_depth, flag, stored, tt_move = entry
            if entry_depth >= depth:
                value = _from_tt(stored, ply)
                if flag == _EXACT:
                    return value
                if flag == _LOWER:
                    alpha = max(alpha, value)
                else:
                    beta = min(beta, value)
                if alpha >= beta:
                    return value

        best_value, best_move = -math.inf, None
        for i in self._order(moves, tt_move, ply):
            delta = self._play(i, p)
            value = -self._negamax(depth - 1, -beta, -alpha, 3 - p, ply + 1)
            self._undo(i, p, delta)
            if value > best_value:
                best_value, best_move = value, i
            if value > alpha:
                alpha = value
            if alpha >= beta:
                killers = self._killers.setdefault(ply, [])
                if i not in killers:
                    killers.insert(0, i)
                    del killers[2:]
                break

        if best_value <= original_alpha:
            flag = _UPPER
        elif best_value >= beta:
            flag = _LOWER
        else:
            flag = _EXACT
        self._tt[key] = (depth, flag, _to_tt(best_value, ply), best_move)
        return best_value


def _to_tt(value: float, ply: int) -> float:
    """Valor para guardar en la tabla: las victorias se miden desde esta posición."""
    if value >= _MATE_BOUND:
        return value + ply
    if value <= -_MATE_BOUND:
        return value - ply
    return value


def _from_tt(value: float, ply: int) -> float:
    """Inverso de _to_tt: las victorias se vuelven a medir desde la raíz."""
    if value >= _MATE_BOUND:
        return value - ply
    if value <= -_MATE_BOUND:
        return value + ply
    return value
