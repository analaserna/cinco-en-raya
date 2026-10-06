import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

import cincoenraya.bots
from cincoenraya.validation import check_source, validate_bot

BOTS_DIR = Path(cincoenraya.bots.__file__).parent
BOT_FILES = sorted(BOTS_DIR.glob("*.py"))


def escribir(tmp_path, codigo, nombre="modulo.py"):
    ruta = tmp_path / nombre
    ruta.write_text(textwrap.dedent(codigo), encoding="utf-8")
    return ruta


@pytest.mark.parametrize("ruta", BOT_FILES, ids=[p.name for p in BOT_FILES])
def test_los_modulos_de_bots_no_usan_codigo_peligroso(ruta):
    assert check_source(ruta) == []


def test_detecta_importaciones_prohibidas(tmp_path):
    ruta = escribir(tmp_path, """
        import os
        import subprocess
        from socket import socket
    """)
    problemas = check_source(ruta)
    assert len(problemas) == 3
    assert all("no se permite importar" in p for p in problemas)


def test_detecta_librerias_externas(tmp_path):
    ruta = escribir(tmp_path, "import numpy\n")
    assert check_source(ruta) == ["línea 1: numpy no pertenece a la biblioteca estándar."]


def test_detecta_llamadas_prohibidas(tmp_path):
    ruta = escribir(tmp_path, """
        datos = open("secreto.txt").read()
        eval("1 + 1")
    """)
    problemas = check_source(ruta)
    assert len(problemas) == 2
    assert any("open()" in p for p in problemas)
    assert any("eval()" in p for p in problemas)


def test_permite_la_biblioteca_estandar_y_el_proyecto(tmp_path):
    ruta = escribir(tmp_path, """
        from __future__ import annotations

        import math
        import random
        from cincoenraya.game import Move
        from . import otro_modulo
    """)
    assert check_source(ruta) == []


def test_validate_bot_informa_del_codigo_peligroso(tmp_path, monkeypatch):
    ruta = escribir(tmp_path, """
        import os

        from cincoenraya.bot import Bot


        class BotPeligroso(Bot):
            name = "Peligroso"

            def choose_move(self, state):
                return state.legal_moves()[0]
    """, nombre="bot_peligroso.py")
    spec = importlib.util.spec_from_file_location("bot_peligroso", ruta)
    modulo = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "bot_peligroso", modulo)
    spec.loader.exec_module(modulo)

    problemas = validate_bot(modulo.BotPeligroso)
    assert any("importar os" in p for p in problemas)