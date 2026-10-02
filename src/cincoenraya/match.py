"""Motor de partidas entre bots."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum

from cincoenraya.bot import Bot
from cincoenraya.errors import InvalidMoveError
from cincoenraya.game import DEFAULT_SIZE, GameState, Move, Player

DEFAULT_TIME_LIMIT = 1.0


class EndReason(Enum):
    """Motivo por el que termina una partida."""

    WIN = "victoria"
    DRAW = "empate"
    ILLEGAL_MOVE = "movimiento ilegal"
    ERROR = "error del bot"
    TIMEOUT = "tiempo agotado"


class BotError(Exception):
    """El bot ha lanzado una excepción al elegir su movimiento."""


class BotTimeoutError(Exception):
    """El bot ha superado el tiempo máximo para elegir su movimiento."""


@dataclass
class MatchResult:
    """Resultado de una partida entre dos bots."""

    black: str
    white: str
    winner: Player | None
    reason: EndReason
    moves: list[Move] = field(default_factory=list)
    final_state: GameState | None = None
    detail: str | None = None

    @property
    def winner_name(self) -> str | None:
        """Nombre del bot ganador, o None si la partida acaba en empate."""
        if self.winner is None:
            return None
        return self.black if self.winner is Player.BLACK else self.white


def ask_bot(bot: Bot, state: GameState, time_limit: float) -> Move:
    """Pide un movimiento al bot con un límite de tiempo.

    El bot se ejecuta en un hilo aparte para poder dejar de esperarle si
    supera el límite. El estado recibido debe ser ya una copia.

    Raises:
        BotTimeoutError: si el bot no responde en time_limit segundos.
        BotError: si el bot lanza cualquier excepción.
    """
    result: dict[str, object] = {}

    def target() -> None:
        try:
            result["move"] = bot.choose_move(state)
        except BaseException as exc:  # ningún fallo del bot debe detener la partida
            result["error"] = exc

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(time_limit)

    if thread.is_alive():
        raise BotTimeoutError(f"{bot.name} superó el límite de {time_limit} s.")
    if "error" in result:
        exc = result["error"]
        raise BotError(f"{type(exc).__name__}: {exc}") from exc
    return result["move"]


def play_match(
    black: Bot,
    white: Bot,
    size: int = DEFAULT_SIZE,
    time_limit: float = DEFAULT_TIME_LIMIT,
) -> MatchResult:
    """Juega una partida completa entre dos bots.

    Un bot que lanza una excepción, supera el tiempo límite o devuelve un
    movimiento ilegal pierde la partida inmediatamente. Ningún fallo de un
    bot interrumpe la ejecución del programa.

    Args:
        black: bot que juega con negras y mueve primero.
        white: bot que juega con blancas.
        size: tamaño del tablero.
        time_limit: segundos máximos por movimiento.

    Returns:
        El resultado de la partida.
    """
    state = GameState(size)
    bots = {Player.BLACK: black, Player.WHITE: white}
    moves: list[Move] = []

    def forfeit(reason: EndReason, detail: str) -> MatchResult:
        return MatchResult(
            black=black.name,
            white=white.name,
            winner=state.current_player.opponent(),
            reason=reason,
            moves=moves,
            final_state=state,
            detail=detail,
        )

    while not state.is_over():
        bot = bots[state.current_player]
        try:
            move = ask_bot(bot, state.copy(), time_limit)
        except BotTimeoutError as exc:
            return forfeit(EndReason.TIMEOUT, str(exc))
        except BotError as exc:
            return forfeit(EndReason.ERROR, str(exc))

        try:
            state.play(move)
        except InvalidMoveError as exc:
            return forfeit(EndReason.ILLEGAL_MOVE, str(exc))
        moves.append(move)

    return MatchResult(
        black=black.name,
        white=white.name,
        winner=state.winner,
        reason=EndReason.DRAW if state.is_draw() else EndReason.WIN,
        moves=moves,
        final_state=state,
    )