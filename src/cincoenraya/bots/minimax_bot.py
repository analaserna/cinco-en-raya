"""Bot minimax con poda alfa-beta, profundidad iterativa y detección de amenazas."""

from __future__ import annotations

import math
import time

from cincoenraya.bot import Bot
from cincoenraya.bots.heuristics import WIN_SCORE, evaluate, makes_five, move_delta, nearby_moves
from cincoenraya.bots.threats import find_vcf, with_turn_passed
from cincoenraya.game import GameState, Move, Player


class _SearchTimeout(Exception):
    """Se ha agotado el tiempo de búsqueda."""


class MinimaxBot(Bot):
    """Bot que combina búsqueda de amenazas forzadas y minimax con poda alfa-beta.

    En cada movimiento, por orden:
        1. Si puede formar cinco en línea, lo hace.
        2. Si el rival puede formar cinco en línea, le bloquea.
        3. Si tiene una victoria por cuatros continuos (VCF), la juega.
        4. Si el rival tendría una VCF, restringe la búsqueda a las jugadas
           que la impiden.
        5. Busca con minimax y poda alfa-beta, con profundidad iterativa
           hasta max_depth o hasta agotar time_limit.

    Las posiciones se valoran con la evaluación por ventanas, calculada de
    forma incremental, y las casillas candidatas también se actualizan de
    forma incremental en cada jugada de la búsqueda.

    Args:
        max_depth: profundidad máxima de búsqueda.
        time_limit: segundos de cálculo por movimiento.
        max_branching: número máximo de jugadas que explora en cada posición.

    Attributes:
        last_depth: profundidad de la última búsqueda completa en el último
            movimiento, o 0 si no hizo falta buscar.
    """

    name = "Minimax"

    def __init__(self, max_depth: int = 6, time_limit: float = 0.5, max_branching: int = 10) -> None:
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.max_branching = max_branching
        self.last_depth = 0
        self._deadline = math.inf

    def choose_move(self, state: GameState) -> Move:
        self.last_depth = 0
        me = state.current_player
        candidates = nearby_moves(state)

        for move in candidates:
            if makes_five(state, move, me):
                return move
        for move in candidates:
            if makes_five(state, move, me.opponent()):
                return move

        start = time.perf_counter()
        winning = find_vcf(state, deadline=start + 0.2 * self.time_limit)
        if winning is not None:
            return winning

        cells = {(move.row, move.col) for move in candidates}
        defenses = self._vcf_defenses(state, cells, start + 0.5 * self.time_limit)
        if defenses:
            cells = defenses

        self._deadline = start + self.time_limit
        best_move = self._ordered_moves(state, cells)[0][1]
        for depth in range(1, self.max_depth + 1):
            try:
                move, value = self._best_move(state, cells, depth, best_move)
            except _SearchTimeout:
                break
            best_move = move
            self.last_depth = depth
            if value >= WIN_SCORE:
                break
        return best_move

    def _vcf_defenses(self, state: GameState, cells: set, deadline: float) -> set | None:
        """Jugadas que impiden una victoria por cuatros continuos del rival.

        Devuelve None si el rival no tiene ninguna VCF. Si la tiene, devuelve
        el conjunto de casillas tras las cuales el rival deja de tenerla, que
        puede estar vacío si ninguna la impide.
        """
        threat = find_vcf(with_turn_passed(state), deadline=deadline)
        if threat is None:
            return None

        options = {(threat.row, threat.col)}
        options.update((move.row, move.col) for _, move in self._ordered_moves(state, cells))
        safe = set()
        for row, col in options:
            if time.perf_counter() > deadline:
                break
            child = state.copy()
            child.play(Move(row, col))
            if find_vcf(child, deadline=deadline) is None:
                safe.add((row, col))
        return safe

    def _check_time(self) -> None:
        """Interrumpe la búsqueda si se ha agotado el tiempo."""
        if time.perf_counter() > self._deadline:
            raise _SearchTimeout

    def _ordered_moves(self, state: GameState, cells: set) -> list[tuple[int, Move]]:
        """Jugadas candidatas con su move_delta para el jugador al que le toca.

        Se devuelven ordenadas de mayor a menor delta y limitadas a max_branching.
        """
        mover = state.current_player
        scored = [(move_delta(state, Move(r, c), mover), Move(r, c)) for r, c in cells]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[: self.max_branching]

    @staticmethod
    def _next_cells(state: GameState, move: Move, cells: set) -> set:
        """Candidatas después de jugar move en state.

        Se quita la casilla jugada y se añaden sus vecinas vacías. Equivale a
        recalcular nearby_moves en la posición siguiente, pero es mucho más rápido.
        """
        new_cells = set(cells)
        new_cells.discard((move.row, move.col))
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                r, c = move.row + d_row, move.col + d_col
                if (
                    (r, c) != (move.row, move.col)
                    and 0 <= r < state.size
                    and 0 <= c < state.size
                    and state.cell(r, c) is None
                ):
                    new_cells.add((r, c))
        return new_cells

    def _best_move(self, state: GameState, cells: set, depth: int, first: Move) -> tuple[Move, float]:
        """Mejor jugada en la raíz de una búsqueda a la profundidad indicada.

        La jugada first, la mejor de la iteración anterior, se explora la primera.
        """
        me = state.current_player
        score = evaluate(state, me)
        moves = self._ordered_moves(state, cells)
        moves.sort(key=lambda item: item[1] != first)

        alpha, beta = -math.inf, math.inf
        best_move, best_value = moves[0][1], -math.inf
        for delta, move in moves:
            value = self._value_after(state, cells, move, delta, depth, alpha, beta, score, me)
            if value > best_value:
                best_move, best_value = move, value
            alpha = max(alpha, best_value)
        return best_move, best_value

    def _value_after(
        self,
        state: GameState,
        cells: set,
        move: Move,
        mover_delta: int,
        depth: int,
        alpha: float,
        beta: float,
        score: int,
        me: Player,
    ) -> float:
        """Valor para me de jugar move en state, mirando depth jugadas en total."""
        mover = state.current_player
        if makes_five(state, move, mover):
            win = WIN_SCORE + depth
            return win if mover is me else -win

        child_score = score + (mover_delta if mover is me else -mover_delta)
        if depth == 1:
            return child_score

        child_cells = self._next_cells(state, move, cells)
        child = state.copy()
        child.play(move)
        return self._search(child, child_cells, depth - 1, alpha, beta, child_score, me)

    def _search(
        self,
        state: GameState,
        cells: set,
        depth: int,
        alpha: float,
        beta: float,
        score: int,
        me: Player,
    ) -> float:
        """Minimax con poda alfa-beta. Devuelve el valor de state para me."""
        self._check_time()
        moves = self._ordered_moves(state, cells)
        if not moves:
            return score

        if state.current_player is me:
            value = -math.inf
            for delta, move in moves:
                value = max(value, self._value_after(state, cells, move, delta, depth, alpha, beta, score, me))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = math.inf
            for delta, move in moves:
                value = min(value, self._value_after(state, cells, move, delta, depth, alpha, beta, score, me))
                beta = min(beta, value)
                if alpha >= beta:
                    break
        return value