import pytest

from cincoenraya import GameOverError, GameState, Move, Player

BLANCAS_LEJOS = [(0, 0), (0, 1), (0, 2), (0, 3)]


def test_victoria_horizontal(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 8)], BLANCAS_LEJOS)
    assert state.winner is Player.BLACK
    assert state.is_over()


def test_victoria_vertical(jugar):
    state = GameState()
    jugar(state, [(r, 7) for r in range(3, 8)], BLANCAS_LEJOS)
    assert state.winner is Player.BLACK


def test_victoria_diagonal(jugar):
    state = GameState()
    jugar(state, [(r, r) for r in range(3, 8)], BLANCAS_LEJOS)
    assert state.winner is Player.BLACK


def test_victoria_antidiagonal(jugar):
    state = GameState()
    jugar(state, [(r, 10 - r) for r in range(3, 8)], BLANCAS_LEJOS)
    assert state.winner is Player.BLACK


def test_cuatro_en_linea_no_gana(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], BLANCAS_LEJOS[:3])
    assert state.winner is None
    assert not state.is_over()
    assert state.current_player is Player.WHITE


def test_ficha_rival_interrumpe_la_linea(jugar):
    state = GameState()
    negras = [(7, 0), (7, 1), (7, 3), (7, 4), (7, 5)]
    blancas = [(7, 2), (0, 0), (0, 1), (0, 2)]
    jugar(state, negras, blancas)
    assert state.winner is None


def test_rellenar_hueco_central_gana(jugar):
    state = GameState()
    negras = [(7, 3), (7, 4), (7, 6), (7, 7), (7, 5)]
    jugar(state, negras, BLANCAS_LEJOS)
    assert state.winner is Player.BLACK


def test_seis_en_linea_tambien_gana(jugar):
    state = GameState()
    negras = [(7, 3), (7, 4), (7, 5), (7, 7), (7, 8), (7, 6)]
    blancas = [(0, 0), (0, 1), (0, 2), (0, 3), (2, 0)]
    jugar(state, negras, blancas)
    assert state.winner is Player.BLACK


def test_ganan_blancas(jugar):
    state = GameState()
    negras = [(0, 0), (0, 2), (0, 4), (2, 0), (2, 2)]
    blancas = [(7, c) for c in range(5)]
    jugar(state, negras, blancas)
    assert state.winner is Player.WHITE


def test_no_se_juega_tras_ganar(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 8)], BLANCAS_LEJOS)
    assert state.legal_moves() == []
    with pytest.raises(GameOverError):
        state.play(Move(10, 10))


def test_el_turno_no_cambia_tras_ganar(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 8)], BLANCAS_LEJOS)
    assert state.current_player is Player.BLACK
    assert state.last_move == Move(7, 7)