import time

from cincoenraya import Bot, Move
from cincoenraya.tournament import main, run_tournament


class PrimeraLibre(Bot):
    name = "Primera libre"

    def choose_move(self, state):
        return state.legal_moves()[0]


class Falla(Bot):
    name = "Falla"

    def choose_move(self, state):
        raise ValueError("fallo intencionado")


class Lento(Bot):
    name = "Lento"

    def choose_move(self, state):
        time.sleep(2)
        return state.legal_moves()[0]


class FueraDelTablero(Bot):
    name = "Fuera del tablero"

    def choose_move(self, state):
        return Move(-1, -1)


class NoSePuedeCrear(Bot):
    name = "No se puede crear"

    def __init__(self):
        raise RuntimeError("fallo en el constructor")

    def choose_move(self, state):
        return state.legal_moves()[0]


class CierraAlCrearse(Bot):
    name = "Cierra al crearse"

    def __init__(self):
        raise SystemExit(1)

    def choose_move(self, state):
        return state.legal_moves()[0]


def clasificacion(result):
    return {s.name: s for s in result.standings}


def test_torneo_con_los_bots_del_proyecto():
    result = run_tournament(games_per_pair=1)
    tabla = clasificacion(result)
    assert {"Aleatorio", "Táctico", "Patrones", "Minimax"} <= set(tabla)
    assert all(s.played == len(tabla) - 1 for s in tabla.values())


def test_cada_pareja_juega_con_ambos_colores():
    result = run_tournament({"A": PrimeraLibre, "B": Falla}, games_per_pair=2)
    assert (result.games[0].black, result.games[0].white) == ("Primera libre", "Falla")
    assert (result.games[1].black, result.games[1].white) == ("Falla", "Primera libre")


def test_numero_de_partidas():
    bots = {"A": PrimeraLibre, "B": Falla, "C": FueraDelTablero}
    result = run_tournament(bots, games_per_pair=2)
    assert len(result.games) == 6
    assert all(s.played == 4 for s in result.standings)


def test_bot_que_lanza_excepciones_pierde_sin_romper_el_torneo():
    result = run_tournament({"A": PrimeraLibre, "B": Falla}, games_per_pair=2)
    tabla = clasificacion(result)
    assert tabla["Falla"].losses == 2
    assert tabla["Falla"].forfeits == 2
    assert tabla["Primera libre"].points == 2


def test_bot_lento_pierde_por_tiempo():
    result = run_tournament({"A": PrimeraLibre, "B": Lento}, games_per_pair=2, time_limit=0.1)
    assert clasificacion(result)["Lento"].forfeits == 2


def test_bot_que_juega_ilegal_pierde():
    result = run_tournament({"A": PrimeraLibre, "B": FueraDelTablero}, games_per_pair=2)
    assert clasificacion(result)["Fuera del tablero"].forfeits == 2


def test_bot_que_no_se_puede_crear_pierde():
    result = run_tournament({"A": PrimeraLibre, "B": NoSePuedeCrear}, games_per_pair=2)
    tabla = clasificacion(result)
    assert tabla["No se puede crear"].forfeits == 2
    assert tabla["Primera libre"].wins == 2
    assert "no se pudo crear" in result.games[0].detail


def test_bot_que_cierra_el_programa_al_crearse_pierde():
    result = run_tournament({"A": PrimeraLibre, "B": CierraAlCrearse}, games_per_pair=2)
    assert clasificacion(result)["Cierra al crearse"].forfeits == 2


def test_clasificacion_ordenada_por_puntos():
    bots = {"A": PrimeraLibre, "B": Falla, "C": FueraDelTablero}
    result = run_tournament(bots, games_per_pair=2)
    assert [s.name for s in result.standings] == ["Primera libre", "Falla", "Fuera del tablero"]
    assert [s.points for s in result.standings] == [4, 1, 1]


def test_tabla_markdown():
    result = run_tournament({"A": PrimeraLibre, "B": Falla}, games_per_pair=2)
    tabla = result.to_markdown()
    assert tabla.startswith("| Pos. | Bot |")
    assert "| 1 | Primera libre | 2 |" in tabla


def test_linea_de_comandos_guarda_la_clasificacion(tmp_path):
    salida = tmp_path / "clasificacion.md"
    assert main(["--games", "1", "--bots", "GreedyBot", "RandomBot", "--output", str(salida)]) == 0
    contenido = salida.read_text(encoding="utf-8")
    assert "| Pos." in contenido
    assert "Táctico" in contenido

class NombrePeligroso(Bot):
    name = "<script>alert(1)</script>"

    def choose_move(self, state):
        return state.legal_moves()[0]


def test_pagina_html_contiene_la_clasificacion():
    result = run_tournament({"A": PrimeraLibre, "B": Falla}, games_per_pair=2)
    pagina = result.to_html("2026-10-08 10:00 UTC")
    assert pagina.startswith("<!DOCTYPE html>")
    assert "Primera libre" in pagina
    assert "2026-10-08 10:00 UTC" in pagina
    assert "error del bot" in pagina


def test_pagina_html_escapa_los_nombres_de_los_bots():
    result = run_tournament({"A": PrimeraLibre, "B": NombrePeligroso}, games_per_pair=1)
    pagina = result.to_html()
    assert "<script>" not in pagina
    assert "&lt;script&gt;" in pagina


def test_linea_de_comandos_genera_la_pagina_html(tmp_path):
    pagina = tmp_path / "public" / "index.html"
    assert main(["--games", "1", "--bots", "GreedyBot", "RandomBot", "--html", str(pagina)]) == 0
    contenido = pagina.read_text(encoding="utf-8")
    assert "Clasificación de bots" in contenido
    assert "Táctico" in contenido