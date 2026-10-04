"""Comprobación automática de que un bot cumple el contrato del API."""

from __future__ import annotations

import inspect
import random

from cincoenraya.bot import Bot
from cincoenraya.game import GameState, Move
from cincoenraya.match import BotError, BotTimeoutError, EndReason, ask_bot, play_match

DEFAULT_TIME_LIMIT = 1.0

_PATRON_CASI_LLENO = ("XXOOX", "OOXXO", "XXOOX", "OOXXO", "XXOOX")


def _mid_game(moves: int = 40) -> GameState:
    """Estado de mitad de partida obtenido con jugadas aleatorias."""
    for seed in range(100):
        rng = random.Random(seed)
        state = GameState()
        while state.move_count < moves and not state.is_over():
            state.play(rng.choice(state.legal_moves()))
        if not state.is_over():
            return state
    raise RuntimeError("No se pudo generar un estado de mitad de partida.")


def _almost_full() -> GameState:
    """Tablero de 5x5 con una sola casilla libre, en turno de negras."""
    black = [(r, c) for r, row in enumerate(_PATRON_CASI_LLENO) for c, s in enumerate(row) if s == "X"]
    white = [(r, c) for r, row in enumerate(_PATRON_CASI_LLENO) for c, s in enumerate(row) if s == "O"]
    black.pop()
    state = GameState(size=5)
    for b, w in zip(black, white):
        state.play(Move(*b))
        state.play(Move(*w))
    return state


def sample_states() -> list[tuple[str, GameState]]:
    """Estados variados en los que todo bot debe devolver un movimiento legal."""
    after_one = GameState()
    after_one.play(Move(7, 7))
    return [
        ("tablero vacío", GameState()),
        ("tras un movimiento", after_one),
        ("mitad de partida", _mid_game()),
        ("tablero 5x5 con una casilla libre", _almost_full()),
    ]


def validate_bot(bot_cls: type, time_limit: float = DEFAULT_TIME_LIMIT) -> list[str]:
    """Comprueba que una clase de bot cumple el contrato del API.

    Comprueba que hereda de Bot, que se puede crear sin argumentos, que
    tiene un nombre propio, que devuelve movimientos legales a tiempo en
    estados variados y que completa partidas contra RandomBot con ambos
    colores y en un tablero pequeño.

    Args:
        bot_cls: la clase del bot, no una instancia.
        time_limit: segundos máximos por movimiento.

    Returns:
        Lista de problemas encontrados. Si está vacía, el bot es válido.
    """
    from cincoenraya.bots.random_bot import RandomBot

    if not (inspect.isclass(bot_cls) and issubclass(bot_cls, Bot)):
        return ["No es una subclase de Bot."]

    try:
        bot = bot_cls()
    except Exception as exc:
        return [f"No se puede crear sin argumentos: {type(exc).__name__}: {exc}"]

    problems = []
    if not isinstance(bot.name, str) or not bot.name.strip() or bot.name == Bot.name:
        problems.append("Debe definir un atributo name propio.")

    for label, state in sample_states():
        try:
            move = ask_bot(bot_cls(), state.copy(), time_limit)
        except BotTimeoutError:
            problems.append(f"{label}: superó el límite de {time_limit} s.")
        except BotError as exc:
            problems.append(f"{label}: lanzó una excepción ({exc}).")
        else:
            if not isinstance(move, Move) or not state.is_legal(move):
                problems.append(f"{label}: devolvió un movimiento ilegal ({move!r}).")

    matches = [
        ("partida con negras", lambda: play_match(bot_cls(), RandomBot(0), time_limit=time_limit)),
        ("partida con blancas", lambda: play_match(RandomBot(0), bot_cls(), time_limit=time_limit)),
        ("partida en tablero 5x5", lambda: play_match(bot_cls(), RandomBot(0), size=5, time_limit=time_limit)),
    ]
    for label, run in matches:
        result = run()
        if result.reason not in (EndReason.WIN, EndReason.DRAW):
            problems.append(f"{label}: perdió por {result.reason.value} ({result.detail}).")

    return problems


def main() -> int:
    """Valida todos los bots del proyecto e imprime un informe."""
    from cincoenraya.registry import available_bots

    exit_code = 0
    for class_name, bot_cls in available_bots().items():
        problems = validate_bot(bot_cls)
        if problems:
            exit_code = 1
            print(f"[FALLO] {class_name}")
            for problem in problems:
                print(f"    - {problem}")
        else:
            print(f"[OK]    {class_name}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())