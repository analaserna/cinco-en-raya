from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

from cincoenraya import Bot, Player  # noqa: E402

APP = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"


class UltimaCasilla(Bot):
    name = "Última casilla"

    def choose_move(self, state):
        return state.legal_moves()[-1]


class Falla(Bot):
    name = "Falla"

    def choose_move(self, state):
        raise ValueError("fallo intencionado")


def iniciar_app(bot=None):
    at = AppTest.from_file(str(APP), default_timeout=30)
    if bot is not None:
        at.session_state["bot"] = bot
    at.run()
    return at


def test_la_app_arranca_sin_errores():
    at = iniciar_app()
    assert not at.exception


def test_el_tablero_empieza_vacio():
    at = iniciar_app()
    assert at.session_state["game"].move_count == 0


def test_el_bot_responde_a_cada_movimiento():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    game = at.session_state["game"]
    assert game.cell(7, 7) is Player.BLACK
    assert game.move_count == 2
    assert game.current_player is Player.BLACK


def test_una_casilla_ocupada_queda_deshabilitada():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    assert at.button(key="cell-7-7").disabled


def test_nueva_partida_vacia_el_tablero():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    at.button(key="nueva-partida").click().run()
    assert at.session_state["game"].move_count == 0


def test_el_humano_puede_ganar_al_bot():
    at = iniciar_app(UltimaCasilla())
    for col in range(3, 8):
        at.button(key=f"cell-7-{col}").click().run()
    assert at.session_state["game"].winner is Player.BLACK
    assert not at.exception


def test_si_el_bot_falla_gana_el_humano():
    at = iniciar_app(Falla())
    at.button(key="cell-7-7").click().run()
    assert at.session_state["game"].winner is Player.BLACK
    assert "Falla" in at.session_state["forfeit"]
    assert not at.exception

def test_se_puede_elegir_el_bot_rival():
    at = iniciar_app()
    at.selectbox(key="opt_bot").select("Aleatorio").run()
    assert at.session_state["bot"].name == "Aleatorio"
    assert at.session_state["game"].move_count == 0


def test_jugando_con_blancas_empieza_el_bot():
    at = iniciar_app()
    at.radio(key="opt_color").set_value("Blancas (empieza el bot)").run()
    game = at.session_state["game"]
    assert at.session_state["human"] is Player.WHITE
    assert game.move_count == 1
    assert game.current_player is Player.WHITE


def test_cambiar_una_opcion_reinicia_la_partida():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    at.selectbox(key="opt_bot").select("Aleatorio").run()
    assert at.session_state["game"].move_count == 0