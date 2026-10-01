import pytest

from cincoenraya import (
    GameOverError,
    GameState,
    InvalidMoveError,
    Move,
    OccupiedCellError,
    OutOfBoundsError,
    Player,
)


def test_jugar_coloca_ficha_del_jugador_actual():
    state = GameState()
    state.play(Move(7, 7))
    assert state.cell(7, 7) is Player.BLACK


def test_turnos_alternan():
    state = GameState()
    state.play(Move(0, 0))
    assert state.current_player is Player.WHITE
    state.play(Move(0, 1))
    assert state.current_player is Player.BLACK


def test_movimientos_legales_disminuyen():
    state = GameState()
    state.play(Move(3, 3))
    assert len(state.legal_moves()) == 15 * 15 - 1
    assert Move(3, 3) not in state.legal_moves()


def test_casilla_ocupada():
    state = GameState()
    state.play(Move(5, 5))
    with pytest.raises(OccupiedCellError):
        state.play(Move(5, 5))


def test_movimiento_ilegal_no_modifica_estado():
    state = GameState()
    state.play(Move(5, 5))
    with pytest.raises(OccupiedCellError):
        state.play(Move(5, 5))
    assert state.current_player is Player.WHITE
    assert state.move_count == 1


@pytest.mark.parametrize("row, col", [(-1, 0), (0, -1), (15, 0), (0, 15)])
def test_fuera_del_tablero(row, col):
    with pytest.raises(OutOfBoundsError):
        GameState().play(Move(row, col))


@pytest.mark.parametrize("move", [None, (3, 3), "3,3"])
def test_movimiento_con_tipo_incorrecto(move):
    with pytest.raises(InvalidMoveError):
        GameState().play(move)


def test_no_se_juega_tras_terminar():
    state = GameState()
    state.winner = Player.BLACK  # simula una partida terminada
    with pytest.raises(GameOverError):
        state.play(Move(0, 0))


def test_errores_heredan_de_invalid_move():
    assert issubclass(OutOfBoundsError, InvalidMoveError)
    assert issubclass(OccupiedCellError, InvalidMoveError)
    assert issubclass(GameOverError, InvalidMoveError)


def test_copia_independiente():
    state = GameState()
    state.play(Move(1, 1))
    clone = state.copy()
    clone.play(Move(2, 2))
    assert state.cell(2, 2) is None
    assert state.move_count == 1
    assert clone.move_count == 2