from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

from cincoenraya import Player  # noqa: E402

APP = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"


def iniciar_app():
    at = AppTest.from_file(str(APP), default_timeout=30)
    at.run()
    return at


def test_la_app_arranca_sin_errores():
    at = iniciar_app()
    assert not at.exception


def test_el_tablero_empieza_vacio():
    at = iniciar_app()
    assert at.session_state["game"].move_count == 0


def test_pulsar_una_casilla_coloca_ficha_y_pasa_el_turno():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    game = at.session_state["game"]
    assert game.cell(7, 7) is Player.BLACK
    assert game.current_player is Player.WHITE


def test_una_casilla_ocupada_queda_deshabilitada():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    assert at.button(key="cell-7-7").disabled


def test_nueva_partida_vacia_el_tablero():
    at = iniciar_app()
    at.button(key="cell-7-7").click().run()
    at.button(key="nueva-partida").click().run()
    assert at.session_state["game"].move_count == 0