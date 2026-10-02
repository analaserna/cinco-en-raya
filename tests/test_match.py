import time

from cincoenraya import Bot, EndReason, Move, Player, play_match
from cincoenraya.bots import RandomBot


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


class DevuelveNone(Bot):
    name = "Devuelve None"

    def choose_move(self, state):
        return None


class SiempreCentro(Bot):
    name = "Siempre centro"

    def choose_move(self, state):
        return Move(7, 7)


class ModificaEstado(Bot):
    name = "Modifica estado"

    def choose_move(self, state):
        move = state.legal_moves()[0]
        state.winner = state.current_player  # intenta declararse ganador
        return move


class SaleDelPrograma(Bot):
    name = "Sale del programa"

    def choose_move(self, state):
        raise SystemExit(1)


def test_partida_normal_entre_random_bots():
    result = play_match(RandomBot(seed=1), RandomBot(seed=2))
    assert result.reason in (EndReason.WIN, EndReason.DRAW)
    assert len(result.moves) == result.final_state.move_count
    assert result.black == "Aleatorio"
    assert result.detail is None


def test_partida_en_tablero_minimo():
    result = play_match(RandomBot(seed=3), RandomBot(seed=4), size=5)
    assert result.final_state.is_over()


def test_bot_que_lanza_excepcion_pierde():
    result = play_match(Falla(), PrimeraLibre())
    assert result.winner is Player.WHITE
    assert result.reason is EndReason.ERROR
    assert "fallo intencionado" in result.detail
    assert result.moves == []


def test_bot_lento_pierde_por_tiempo():
    result = play_match(PrimeraLibre(), Lento(), time_limit=0.1)
    assert result.winner is Player.BLACK
    assert result.reason is EndReason.TIMEOUT
    assert len(result.moves) == 1


def test_movimiento_fuera_del_tablero_pierde():
    result = play_match(FueraDelTablero(), PrimeraLibre())
    assert result.winner is Player.WHITE
    assert result.reason is EndReason.ILLEGAL_MOVE


def test_devolver_algo_que_no_es_un_move_pierde():
    result = play_match(PrimeraLibre(), DevuelveNone())
    assert result.winner is Player.BLACK
    assert result.reason is EndReason.ILLEGAL_MOVE


def test_jugar_en_casilla_ocupada_pierde():
    result = play_match(PrimeraLibre(), SiempreCentro())
    # negras (0, 0), blancas (7, 7), negras (0, 1), blancas (7, 7) ocupada
    assert result.winner is Player.BLACK
    assert result.reason is EndReason.ILLEGAL_MOVE
    assert len(result.moves) == 3


def test_bot_no_puede_modificar_la_partida_real():
    result = play_match(ModificaEstado(), ModificaEstado())
    assert len(result.moves) > 1
    assert result.reason is EndReason.WIN


def test_bot_que_intenta_cerrar_el_programa_pierde():
    result = play_match(SaleDelPrograma(), PrimeraLibre())
    assert result.winner is Player.WHITE
    assert result.reason is EndReason.ERROR
    assert "SystemExit" in result.detail


def test_nombre_del_ganador():
    result = play_match(Falla(), PrimeraLibre())
    assert result.winner_name == "Primera libre"