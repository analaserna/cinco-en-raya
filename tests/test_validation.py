import time

from cincoenraya import Bot, Move
from cincoenraya.bots import GreedyBot, RandomBot
from cincoenraya.validation import sample_states, validate_bot


class NoEsUnBot:
    name = "No es un bot"

    def choose_move(self, state):
        return state.legal_moves()[0]


class NecesitaArgumentos(Bot):
    name = "Necesita argumentos"

    def __init__(self, profundidad):
        self.profundidad = profundidad

    def choose_move(self, state):
        return state.legal_moves()[0]


class SinNombre(Bot):
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


class SiempreCentro(Bot):
    name = "Siempre centro"

    def choose_move(self, state):
        return Move(7, 7)


class SuponeTablero15(Bot):
    name = "Supone tablero 15"

    def choose_move(self, state):
        for row in range(15):
            for col in range(15):
                if state.cell(row, col) is None:
                    return Move(row, col)


def test_los_bots_del_proyecto_son_validos():
    assert validate_bot(RandomBot) == []
    assert validate_bot(GreedyBot) == []


def test_detecta_clase_que_no_hereda_de_bot():
    assert validate_bot(NoEsUnBot) == ["No es una subclase de Bot."]


def test_detecta_bot_que_necesita_argumentos():
    problems = validate_bot(NecesitaArgumentos)
    assert len(problems) == 1
    assert "sin argumentos" in problems[0]


def test_detecta_bot_sin_nombre():
    assert validate_bot(SinNombre) == ["Debe definir un atributo name propio."]


def test_detecta_bot_que_lanza_excepciones():
    problems = validate_bot(Falla)
    assert any("excepción" in p for p in problems)
    assert any("error del bot" in p for p in problems)


def test_detecta_bot_lento():
    problems = validate_bot(Lento, time_limit=0.1)
    assert any("límite" in p for p in problems)
    assert any("tiempo agotado" in p for p in problems)


def test_detecta_movimientos_fuera_del_tablero():
    problems = validate_bot(FueraDelTablero)
    assert any("movimiento ilegal" in p for p in problems)


def test_detecta_bot_que_repite_casilla():
    problems = validate_bot(SiempreCentro)
    assert any(p.startswith("tras un movimiento") for p in problems)


def test_detecta_bot_que_no_respeta_el_tamano_del_tablero():
    problems = validate_bot(SuponeTablero15)
    assert any("5x5" in p for p in problems)


def test_los_estados_de_prueba_tienen_movimientos_legales():
    for label, state in sample_states():
        assert not state.is_over(), label
        assert state.legal_moves(), label