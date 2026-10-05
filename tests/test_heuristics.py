import random

import pytest

from cincoenraya import GameState, Move, Player
from cincoenraya.bots.heuristics import (
    WIN_SCORE,
    evaluate,
    makes_five,
    move_delta,
    nearby_moves,
    window_score,
    windows,
    windows_through,
)


def posicion_intermedia(moves=20):
    for seed in range(100):
        rng = random.Random(seed)
        state = GameState()
        while state.move_count < moves and not state.is_over():
            state.play(rng.choice(state.legal_moves()))
        if not state.is_over():
            return state
    raise RuntimeError("No se pudo generar la posición")


def test_numero_de_ventanas():
    assert len(windows(15)) == 572
    assert len(windows(5)) == 12


def test_ventanas_que_pasan_por_cada_casilla():
    assert len(windows_through(15)[(7, 7)]) == 20
    assert len(windows_through(15)[(0, 0)]) == 3


@pytest.mark.parametrize(
    "mine, theirs, expected",
    [(0, 0, 0), (2, 0, 10), (0, 3, -100), (2, 1, 0), (4, 0, 10_000), (5, 0, WIN_SCORE)],
)
def test_valor_de_una_ventana(mine, theirs, expected):
    assert window_score(mine, theirs) == expected


def test_tablero_vacio_vale_cero():
    assert evaluate(GameState(), Player.BLACK) == 0


def test_evaluacion_simetrica():
    state = GameState()
    for row, col in [(7, 7), (7, 8), (8, 8), (6, 6)]:
        state.play(Move(row, col))
    assert evaluate(state, Player.BLACK) == -evaluate(state, Player.WHITE)


def test_fichas_alineadas_valen_mas_que_separadas():
    juntas = GameState()
    for row, col in [(7, 7), (0, 0), (7, 8)]:
        juntas.play(Move(row, col))
    separadas = GameState()
    for row, col in [(7, 7), (0, 0), (12, 2)]:
        separadas.play(Move(row, col))
    assert evaluate(juntas, Player.BLACK) > evaluate(separadas, Player.BLACK)


def test_el_calculo_incremental_coincide_con_evaluar_todo():
    state = posicion_intermedia()
    for move in nearby_moves(state):
        if makes_five(state, move, state.current_player):
            continue
        after = state.copy()
        after.play(move)
        for player in (Player.BLACK, Player.WHITE):
            esperado = evaluate(after, player) - evaluate(state, player)
            assert move_delta(state, move, player) == esperado


def test_casillas_cercanas_con_tablero_vacio():
    assert nearby_moves(GameState()) == [Move(7, 7)]


def test_casillas_cercanas_tras_un_movimiento():
    state = GameState()
    state.play(Move(7, 7))
    assert len(nearby_moves(state)) == 8


def test_casillas_cercanas_en_una_esquina():
    state = GameState()
    state.play(Move(0, 0))
    assert set(nearby_moves(state)) == {Move(0, 1), Move(1, 0), Move(1, 1)}


def test_detecta_jugadas_ganadoras(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], [(0, 0), (0, 2), (0, 4), (0, 6)])
    assert makes_five(state, Move(7, 7), Player.BLACK)
    assert makes_five(state, Move(7, 2), Player.BLACK)
    assert not makes_five(state, Move(8, 8), Player.BLACK)