import pytest

from cincoenraya import GameOverError, GameState, Move, Player

BLANCAS_ABAJO = [(14, 0), (14, 1), (14, 2), (14, 3)]

PATRON_EMPATE = [
    "XXOOX",
    "OOXXO",
    "XXOOX",
    "OOXXO",
    "XXOOX",
]


def posiciones(patron, simbolo):
    return [(r, c) for r, fila in enumerate(patron) for c, s in enumerate(fila) if s == simbolo]


def test_victoria_en_borde_superior(jugar):
    state = GameState()
    jugar(state, [(0, c) for c in range(10, 15)], BLANCAS_ABAJO)
    assert state.winner is Player.BLACK


def test_victoria_en_borde_derecho(jugar):
    state = GameState()
    jugar(state, [(r, 14) for r in range(10, 15)], [(0, 0), (0, 1), (0, 2), (0, 3)])
    assert state.winner is Player.BLACK


def test_victoria_diagonal_desde_esquina(jugar):
    state = GameState()
    jugar(state, [(r, r) for r in range(5)], BLANCAS_ABAJO)
    assert state.winner is Player.BLACK


def test_victoria_antidiagonal_hasta_esquina(jugar):
    state = GameState()
    jugar(state, [(r, 14 - r) for r in range(5)], BLANCAS_ABAJO)
    assert state.winner is Player.BLACK


def test_la_linea_no_continua_en_la_fila_siguiente(jugar):
    state = GameState()
    jugar(state, [(7, 12), (7, 13), (7, 14), (8, 0), (8, 1)], BLANCAS_ABAJO)
    assert state.winner is None


def test_victoria_en_tablero_minimo(jugar):
    state = GameState(size=5)
    jugar(state, [(r, r) for r in range(5)], [(0, 1), (0, 2), (0, 3), (0, 4)])
    assert state.winner is Player.BLACK


def test_empate_con_tablero_lleno(jugar):
    state = GameState(size=5)
    jugar(state, posiciones(PATRON_EMPATE, "X"), posiciones(PATRON_EMPATE, "O"))
    assert state.is_full()
    assert state.is_over()
    assert state.is_draw()
    assert state.winner is None
    assert state.legal_moves() == []
    with pytest.raises(GameOverError):
        state.play(Move(0, 0))


def test_no_es_empate_al_empezar():
    assert not GameState().is_draw()


def test_victoria_no_es_empate(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 8)], [(0, 0), (0, 1), (0, 2), (0, 3)])
    assert not state.is_draw()