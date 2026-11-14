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
:root {{ --madera: #dcb35c; --marron: #5a4320; --fondo: #faf6ee; --texto: #2b2b2b; --gris: #6b6b6b; --verde: #2e7d32; --rojo: #c62828; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--fondo); color: var(--texto); }}
header {{ background: var(--marron); color: #fff; padding: 2rem 1rem; }}
header .contenido, main {{ max-width: 960px; margin: 0 auto; }}
header h1 {{ margin: 0 0 .3rem; font-size: 2rem; }}
header p {{ margin: .2rem 0; opacity: .9; }}
nav {{ margin-top: 1rem; display: flex; flex-wrap: wrap; gap: .5rem; }}
nav a {{ color: var(--marron); background: var(--madera); padding: .4rem .8rem; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: .9rem; }}
nav a:hover {{ background: #e8c77a; }}
main {{ padding: 1.5rem 1rem 3rem; }}
.resumen {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem; }}
.tarjeta {{ background: #fff; border-radius: 10px; padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0, 0, 0, .08); }}
.tarjeta .valor {{ font-size: 1.6rem; font-weight: 700; color: var(--marron); }}
.tarjeta .etiqueta {{ color: var(--gris); font-size: .9rem; }}
h2 {{ color: var(--marron); margin: 2rem 0 .8rem; }}
.explicacion {{ color: var(--gris); font-size: .9rem; margin: 0 0 1rem; }}
.tabla {{ overflow-x: auto; background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0, 0, 0, .08); }}
table {{ border-collapse: collapse; width: 100%; font-size: .95rem; }}
th, td {{ padding: .6rem .8rem; border-bottom: 1px solid #eee; white-space: nowrap; text-align: left; }}
th {{ background: #f3ead8; color: var(--marron); font-weight: 600; }}
tr:last-child td {{ border-bottom: none; }}
th.num, td.num {{ text-align: right; }}
th.centro, td.centro {{ text-align: center; }}
.pos {{ display: inline-flex; align-items: center; justify-content: center; width: 1.9rem; height: 1.9rem; border-radius: 50%; background: #eee; font-weight: 700; }}
.pos-1 {{ background: #f2c94c; }}
.pos-2 {{ background: #c9ced6; }}
.pos-3 {{ background: #d9a066; }}
.bot {{ font-weight: 600; }}
.puntos {{ font-weight: 700; font-size: 1.05rem; }}
.barra {{ position: relative; display: inline-block; width: 110px; height: .6rem; margin-right: .5rem; background: #eee; border-radius: 999px; overflow: hidden; vertical-align: middle; }}
.barra span {{ position: absolute; top: 0; bottom: 0; left: 0; background: var(--verde); border-radius: 999px; }}
.etiqueta-motivo {{ display: inline-block; padding: .15rem .55rem; border-radius: 999px; font-size: .8rem; font-weight: 600; }}
.motivo-ok {{ background: #e3f2e5; color: var(--verde); }}
.motivo-empate {{ background: #eee; color: var(--gris); }}
.motivo-fallo {{ background: #fdecea; color: var(--rojo); }}
.descalif {{ color: var(--rojo); font-weight: 700; }}
.ganador {{ font-weight: 700; }}
.detalle {{ color: var(--gris); font-size: .85rem; white-space: normal; min-width: 200px; }}
footer {{ text-align: center; color: var(--gris); font-size: .85rem; padding: 1rem; }}
</style>
</head>
<body>
<header>
<div class="contenido">
<h1>Clasificación de bots</h1>
<p>Torneo todos contra todos del proyecto cinco en raya.</p>
{date_line}
<nav>
<a href="https://cinco-en-raya-cunef.streamlit.app">Jugar en la web</a>
<a href="https://cinco-en-raya.readthedocs.io/es/latest/">Documentación</a>
<a href="https://cinco-en-raya.readthedocs.io/es/latest/tutorial-bot/">Crea tu bot</a>
<a href="https://github.com/analaserna/cinco-en-raya">Repositorio</a>
</nav>
</div>
</header>
<main>
<section class="resumen">
<div class="tarjeta"><div class="valor">{leader}</div><div class="etiqueta">Líder</div></div>
<div class="tarjeta"><div class="valor">{n_bots}</div><div class="etiqueta">Bots</div></div>
<div class="tarjeta"><div class="valor">{n_games}</div><div class="etiqueta">Partidas</div></div>
<div class="tarjeta"><div class="valor">{n_forfeits}</div><div class="etiqueta">Derrotas por fallo</div></div>
</section>
<h2>Clasificación</h2>
<p class="explicacion">Cada pareja de bots juega con ambos colores. Victoria: 1 punto; empate: 0,5 puntos. La columna "Descalif." cuenta las derrotas por error, tiempo agotado o movimiento ilegal.</p>
<div class="tabla">
<table>
<thead><tr><th class="centro">Pos.</th><th>Bot</th><th class="num">Puntos</th><th>Victorias</th><th class="num">PJ</th><th class="num">G</th><th class="num">E</th><th class="num">P</th><th class="num">Descalif.</th></tr></thead>
<tbody>
{standing_rows}
</tbody>
</table>
</div>
<h2>Partidas</h2>
<div class="tabla">
<table>
<thead><tr><th>Negras</th><th>Blancas</th><th>Ganador</th><th>Resultado</th><th class="num">Jugadas</th><th>Detalle</th></tr></thead>
<tbody>
{game_rows}
</tbody>
</table>
</div>
</main>
<footer>Página generada automáticamente con GitHub Actions tras cada cambio en la rama main.</footer>
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

        standing_rows = []
        for position, s in enumerate(self.standings, start=1):
            rate = 100 * s.wins / s.played if s.played else 0
            pos_class = f"pos pos-{position}" if position <= 3 else "pos"
            forfeits = f'<span class="descalif">{s.forfeits}</span>' if s.forfeits else "0"
            standing_rows.append(
                f'<tr><td class="centro"><span class="{pos_class}">{position}</span></td>'
                f'<td class="bot">{esc(s.name)}</td>'
                f'<td class="num puntos">{s.points:g}</td>'
                f'<td><span class="barra"><span style="width: {rate:.0f}%"></span></span>{rate:.0f} %</td>'
                f'<td class="num">{s.played}</td><td class="num">{s.wins}</td>'
                f'<td class="num">{s.draws}</td><td class="num">{s.losses}</td>'
                f'<td class="num">{forfeits}</td></tr>'
            )

        game_rows = []
        for g in self.games:
            if g.reason is EndReason.WIN:
                reason_class = "motivo-ok"
            elif g.reason is EndReason.DRAW:
                reason_class = "motivo-empate"
            else:
                reason_class = "motivo-fallo"
            black, white = esc(g.black), esc(g.white)
            if g.winner is Player.BLACK:
                black = f'<span class="ganador">{black}</span>'
            elif g.winner is Player.WHITE:
                white = f'<span class="ganador">{white}</span>'
            winner = esc(g.winner_name) if g.winner_name else "Sin ganador"
            game_rows.append(
                f"<tr><td>{black}</td><td>{white}</td><td>{winner}</td>"
                f'<td><span class="etiqueta-motivo {reason_class}">{esc(g.reason.value)}</span></td>'
                f'<td class="num">{len(g.moves)}</td>'
                f'<td class="detalle">{esc(g.detail or "")}</td></tr>'
            )

        date_line = f"<p>Actualizada: {esc(generated_at)}</p>" if generated_at else ""
        leader = esc(self.standings[0].name) if self.standings else "-"
        return HTML_TEMPLATE.format(
            date_line=date_line,
            leader=leader,
            n_bots=len(self.standings),
            n_games=len(self.games),
            n_forfeits=sum(s.forfeits for s in self.standings),
            standing_rows="\n".join(standing_rows),
            game_rows="\n".join(game_rows),
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
    parser.add_argument("--bots", nargs="+", help="Nombres de clase de los bots que participan (por defecto, todos).")
    args = parser.parse_args(argv)

    def show(result: MatchResult) -> None:
        winner = result.winner_name or "sin ganador"
        print(f"{result.black} vs {result.white}: {winner} ({result.reason.value})")

    bots = available_bots()
    if args.bots:
        bots = {name: cls for name, cls in bots.items() if name in args.bots}

    result = run_tournament(
        bots,
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