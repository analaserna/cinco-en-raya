"""Torneo todos contra todos entre los bots del proyecto."""

from __future__ import annotations

import argparse
import html
import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from cincoenraya.game import DEFAULT_SIZE, Player
from cincoenraya.match import DEFAULT_TIME_LIMIT, EndReason, MatchResult, play_match
from cincoenraya.registry import available_bots

FORFEIT_REASONS = (EndReason.ERROR, EndReason.TIMEOUT, EndReason.ILLEGAL_MOVE)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clasificación de bots - Cinco en raya</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
h1 {{ margin-bottom: 0.2rem; }}
.fecha {{ color: #666; margin-top: 0; }}
.tabla {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }}
th {{ background: #f4f4f4; }}
.clasificacion td:nth-child(n+3) {{ text-align: right; }}
</style>
</head>
<body>
<h1>Clasificación de bots</h1>
{date_line}
<p>Torneo todos contra todos entre los bots del proyecto
<a href="https://github.com/analaserna/cinco-en-raya">cinco-en-raya</a>.
Cada pareja juega con ambos colores. Victoria: 1 punto; empate: 0,5 puntos.
La columna "Descalif." cuenta las derrotas por error, tiempo agotado o movimiento ilegal.</p>
<div class="tabla">
<table class="clasificacion">
<thead><tr><th>Pos.</th><th>Bot</th><th>Puntos</th><th>PJ</th><th>G</th><th>E</th><th>P</th><th>Descalif.</th></tr></thead>
<tbody>
{standing_rows}
</tbody>
</table>
</div>
<h2>Partidas</h2>
<div class="tabla">
<table>
<thead><tr><th>Negras</th><th>Blancas</th><th>Ganador</th><th>Motivo</th><th>Movimientos</th><th>Detalle</th></tr></thead>
<tbody>
{game_rows}
</tbody>
</table>
</div>
</body>
</html>
"""


@dataclass
class Standing:
    """Resultados acumulados de un bot en el torneo."""

    name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    forfeits: int = 0

    @property
    def points(self) -> float:
        """Puntos: 1 por victoria y 0,5 por empate."""
        return self.wins + 0.5 * self.draws


@dataclass
class TournamentResult:
    """Clasificación final y lista de partidas del torneo."""

    standings: list[Standing] = field(default_factory=list)
    games: list[MatchResult] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Devuelve la clasificación como tabla en Markdown."""
        lines = [
            "| Pos. | Bot | Puntos | PJ | G | E | P | Descalif. |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
        for position, s in enumerate(self.standings, start=1):
            lines.append(
                f"| {position} | {s.name} | {s.points:g} | {s.played} | "
                f"{s.wins} | {s.draws} | {s.losses} | {s.forfeits} |"
            )
        return "\n".join(lines)

    def to_html(self, generated_at: str | None = None) -> str:
        """Devuelve una página HTML independiente con la clasificación y las partidas.

        Los nombres y textos de los bots se escapan para que no puedan
        inyectar código en la página.
        """
        esc = html.escape
        standing_rows = "\n".join(
            f"<tr><td>{position}</td><td>{esc(s.name)}</td><td>{s.points:g}</td>"
            f"<td>{s.played}</td><td>{s.wins}</td><td>{s.draws}</td>"
            f"<td>{s.losses}</td><td>{s.forfeits}</td></tr>"
            for position, s in enumerate(self.standings, start=1)
        )
        game_rows = "\n".join(
            f"<tr><td>{esc(g.black)}</td><td>{esc(g.white)}</td>"
            f"<td>{esc(g.winner_name or 'Sin ganador')}</td><td>{esc(g.reason.value)}</td>"
            f"<td>{len(g.moves)}</td><td>{esc(g.detail or '')}</td></tr>"
            for g in self.games
        )
        date_line = f'<p class="fecha">Actualizada: {esc(generated_at)}</p>' if generated_at else ""
        return HTML_TEMPLATE.format(
            date_line=date_line,
            standing_rows=standing_rows,
            game_rows=game_rows,
        )


def bot_name(bot_cls: type) -> str:
    """Nombre visible de una clase de bot."""
    name = getattr(bot_cls, "name", None)
    return name if isinstance(name, str) and name.strip() else bot_cls.__name__


def play_tournament_game(
    black_cls: type,
    white_cls: type,
    size: int = DEFAULT_SIZE,
    time_limit: float = DEFAULT_TIME_LIMIT,
) -> MatchResult:
    """Juega una partida del torneo sin que ningún fallo de los bots la interrumpa.

    Si un bot no se puede crear, pierde la partida. Si no se puede crear
    ninguno de los dos, ambos pierden.
    """
    black_name, white_name = bot_name(black_cls), bot_name(white_cls)
    bots = {}
    failures = {}
    for player, cls in ((Player.BLACK, black_cls), (Player.WHITE, white_cls)):
        try:
            bots[player] = cls()
        except (Exception, SystemExit) as exc:
            failures[player] = f"{bot_name(cls)} no se pudo crear ({type(exc).__name__}: {exc})."

    if failures:
        if len(failures) == 2:
            winner = None
        else:
            winner = Player.WHITE if Player.BLACK in failures else Player.BLACK
        return MatchResult(
            black=black_name,
            white=white_name,
            winner=winner,
            reason=EndReason.ERROR,
            detail=" ".join(failures.values()),
        )

    try:
        return play_match(bots[Player.BLACK], bots[Player.WHITE], size=size, time_limit=time_limit)
    except Exception as exc:
        return MatchResult(
            black=black_name,
            white=white_name,
            winner=None,
            reason=EndReason.ERROR,
            detail=f"Error interno del torneo ({type(exc).__name__}: {exc}).",
        )


def _record(standings: dict[str, Standing], black: str, white: str, result: MatchResult) -> None:
    """Anota el resultado de una partida en la clasificación."""
    for name in (black, white):
        standings[name].played += 1

    if result.winner is None:
        if result.reason in FORFEIT_REASONS:
            for name in (black, white):
                standings[name].losses += 1
                standings[name].forfeits += 1
        else:
            standings[black].draws += 1
            standings[white].draws += 1
        return

    winner, loser = (black, white) if result.winner is Player.BLACK else (white, black)
    standings[winner].wins += 1
    standings[loser].losses += 1
    if result.reason in FORFEIT_REASONS:
        standings[loser].forfeits += 1


def run_tournament(
    bots: dict[str, type] | None = None,
    games_per_pair: int = 2,
    size: int = DEFAULT_SIZE,
    time_limit: float = DEFAULT_TIME_LIMIT,
    on_game: Callable[[MatchResult], None] | None = None,
) -> TournamentResult:
    """Enfrenta a todos los bots entre sí y devuelve la clasificación.

    Cada pareja de bots juega games_per_pair partidas, alternando los colores.
    Un bot que falla, supera el tiempo límite o juega un movimiento ilegal
    pierde esa partida, pero el torneo continúa.

    Args:
        bots: diccionario {nombre: clase}. Por defecto, todos los bots del proyecto.
        games_per_pair: partidas que juega cada pareja de bots.
        size: tamaño del tablero.
        time_limit: segundos máximos por movimiento.
        on_game: función opcional que se llama tras cada partida con su resultado.

    Returns:
        La clasificación, ordenada por puntos, victorias y nombre, y la lista de partidas.
    """
    if bots is None:
        bots = available_bots()
    classes = list(bots.values())
    standings = {bot_name(cls): Standing(bot_name(cls)) for cls in classes}
    games = []

    for first, second in itertools.combinations(classes, 2):
        for game_index in range(games_per_pair):
            black, white = (first, second) if game_index % 2 == 0 else (second, first)
            result = play_tournament_game(black, white, size, time_limit)
            games.append(result)
            _record(standings, bot_name(black), bot_name(white), result)
            if on_game is not None:
                on_game(result)

    ranking = sorted(standings.values(), key=lambda s: (-s.points, -s.wins, s.name))
    return TournamentResult(standings=ranking, games=games)


def main(argv: list[str] | None = None) -> int:
    """Ejecuta el torneo desde la línea de comandos."""
    parser = argparse.ArgumentParser(description="Torneo todos contra todos entre los bots del proyecto.")
    parser.add_argument("--games", type=int, default=2, help="Partidas por pareja de bots.")
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE, help="Tamaño del tablero.")
    parser.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT, help="Segundos por movimiento.")
    parser.add_argument("--output", type=Path, help="Archivo Markdown donde guardar la clasificación.")
    parser.add_argument("--html", type=Path, help="Archivo HTML donde guardar la página de la clasificación.")
    args = parser.parse_args(argv)

    def show(result: MatchResult) -> None:
        winner = result.winner_name or "sin ganador"
        print(f"{result.black} vs {result.white}: {winner} ({result.reason.value})")

    result = run_tournament(
        games_per_pair=args.games,
        size=args.size,
        time_limit=args.time_limit,
        on_game=show,
    )
    table = result.to_markdown()
    print()
    print(table)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(table + "\n", encoding="utf-8")
    if args.html is not None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(result.to_html(generated_at), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())