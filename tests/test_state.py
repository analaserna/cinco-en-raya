import pytest

from cincoenraya import GameState, Move, Player


def test_tablero_inicial_vacio():
    state = GameState()
    assert state.size == 15
    assert all(state.cell(r, c) is None for r in range(15) for c in range(15))


def test_empiezan_negras():
    assert GameState().current_player is Player.BLACK


def test_partida_inicial_no_terminada():
    state = GameState()
    assert not state.is_over()
    assert state.winner is None


def test_movimientos_legales_iniciales():
    assert len(GameState().legal_moves()) == 15 * 15


def test_tablero_personalizado():
    assert len(GameState(size=9).legal_moves()) == 81


def test_tablero_demasiado_pequeno():
    with pytest.raises(ValueError):
        GameState(size=4)


@pytest.mark.parametrize("row, col", [(-1, 0), (0, -1), (15, 0), (0, 15)])
def test_casillas_fuera_del_tablero_no_son_legales(row, col):
    assert not GameState().is_legal(Move(row, col))


def test_coordenadas_no_enteras_no_son_legales():
    assert not GameState().is_legal(Move(1.5, 2))


def test_oponente():
    assert Player.BLACK.opponent() is Player.WHITE
    assert Player.WHITE.opponent() is Player.BLACK