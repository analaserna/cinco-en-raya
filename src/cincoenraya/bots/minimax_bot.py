"""Bot minimax con poda alfa-beta sobre la evaluación por ventanas."""

from __future__ import annotations

import math

from cincoenraya.bot import Bot
from cincoenraya.bots.heuristics import WIN_SCORE, evaluate, makes_five, move_delta, nearby_moves
from cincoenraya.game import GameState, Move, Player


class MinimaxBot(Bot):
    """Bot que busca varias jugadas hacia delante con minimax y poda alfa-beta.

    Antes de buscar, gana si puede y bloquea si el rival puede ganar. En la
    búsqueda, las posiciones finales se valoran con la evaluación por
    ventanas, calculada de forma incremental con move_delta. En cada
    posición solo se exploran las max_branching casillas candidatas más
    prometedoras, ordenadas de mejor a peor para que la poda sea eficaz.

    Args:
        depth: número de jugadas (propias y del rival) que mira hacia delante.
        max_branching: número máximo de jugadas que explora en cada posición.
    """

    name = "Minimax"

    def __init__(self, depth: int = 2, max_branching: int = 10) -> None:
        self.depth = depth
        self.max_branching = max_branching

    def choose_move(self, state: GameState) -> Move:
        me = state.current_player
        candidates = nearby_moves(state)

        for move in candidates:
            if makes_five(state, move, me):
                return move
        for move in candidates:
            if makes_five(state, move, me.opponent()):
                return move

        best_move, _ = self._best_move(state, self.depth)
        return best_move

    def _ordered_moves(self, state: GameState) -> list[tuple[int, Move]]:
        """Jugadas candidatas con su move_delta para el jugador al que le toca.

        Se devuelven ordenadas de mayor a menor delta y limitadas a max_branching.
        """
        mover = state.current_player
        scored = [(move_delta(state, move, mover), move) for move in nearby_moves(state)]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[: self.max_branching]

    def _best_move(self, state: GameState, depth: int) -> tuple[Move, float]:
        """Mejor jugada en la raíz de la búsqueda y su valor."""
        me = state.current_player
        score = evaluate(state, me)
        alpha, beta = -math.inf, math.inf
        best_move, best_value = None, -math.inf
        for delta, move in self._ordered_moves(state):
            value = self._value_after(state, move, delta, depth, alpha, beta, score, me)
            if value > best_value:
                best_move, best_value = move, value
            alpha = max(alpha, best_value)
        return best_move, best_value

    def _value_after(
        self,
        state: GameState,
        move: Move,
        mover_delta: int,
        depth: int,
        alpha: float,
        beta: float,
        score: int,
        me: Player,
    ) -> float:
        """Valor para me de jugar move en state, mirando depth jugadas en total.

        score es la evaluación de state para me. mover_delta es el move_delta
        de la jugada para el jugador que la hace.
        """
        mover = state.current_player
        if makes_five(state, move, mover):
            win = WIN_SCORE + depth
            return win if mover is me else -win

        child_score = score + (mover_delta if mover is me else -mover_delta)
        if depth == 1:
            return child_score

        child = state.copy()
        child.play(move)
        return self._search(child, depth - 1, alpha, beta, child_score, me)

    def _search(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        score: int,
        me: Player,
    ) -> float:
        """Minimax con poda alfa-beta. Devuelve el valor de state para me."""
        moves = self._ordered_moves(state)
        if not moves:
            return score

        if state.current_player is me:
            value = -math.inf
            for delta, move in moves:
                value = max(value, self._value_after(state, move, delta, depth, alpha, beta, score, me))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = math.inf
            for delta, move in moves:
                value = min(value, self._value_after(state, move, delta, depth, alpha, beta, score, me))
                beta = min(beta, value)
                if alpha >= beta:
                    break
        return value