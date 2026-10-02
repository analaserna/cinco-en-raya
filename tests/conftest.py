import pytest

from cincoenraya import Move


@pytest.fixture
def jugar():
    """Devuelve una función que juega alternando negras y blancas.

    Juega negras[0], blancas[0], negras[1], blancas[1], ...
    Si negras tiene un movimiento más que blancas, la última jugada es de negras.
    """

    def _jugar(state, negras, blancas):
        for i, (row, col) in enumerate(negras):
            state.play(Move(row, col))
            if i < len(blancas):
                state.play(Move(*blancas[i]))

    return _jugar