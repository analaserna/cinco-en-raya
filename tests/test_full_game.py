import random

import pytest

from cincoenraya import GameState


def jugar_partida_aleatoria(size, seed):
    rng = random.Random(seed)
    state = GameState(size=size)
    while not state.is_over():
        state.play(rng.choice(state.legal_moves()))
    return state


@pytest.mark.parametrize("seed", range(20))
def test_partida_aleatoria_termina(seed):
    state = jugar_partida_aleatoria(15, seed)
    assert state.is_over()
    assert (state.winner is not None) != state.is_draw()
    assert state.legal_moves() == []


@pytest.mark.parametrize("seed", range(20))
def test_partida_aleatoria_tablero_minimo(seed):
    state = jugar_partida_aleatoria(5, seed)
    assert state.is_over()


@pytest.mark.parametrize("seed", range(5))
def test_numero_de_fichas_coincide_con_movimientos(seed):
    state = jugar_partida_aleatoria(15, seed)
    fichas = sum(
        state.cell(r, c) is not None for r in range(state.size) for c in range(state.size)
    )
    assert fichas == state.move_count