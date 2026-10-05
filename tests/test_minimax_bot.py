from cincoenraya import GameState, Move, Player, play_match
from cincoenraya.bots import MinimaxBot, RandomBot

BLANCAS_SUELTAS = [(0, 0), (0, 2), (0, 4), (0, 6)]
NEGRAS_SUELTAS = [(14, 0), (14, 2), (14, 4), (14, 6)]


def test_primer_movimiento_en_el_centro():
    assert MinimaxBot().choose_move(GameState()) == Move(7, 7)


def test_gana_cuando_puede(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], BLANCAS_SUELTAS)
    assert MinimaxBot().choose_move(state) in (Move(7, 2), Move(7, 7))


def test_bloquea_un_cuatro_del_rival(jugar):
    state = GameState()
    jugar(state, NEGRAS_SUELTAS, [(7, c) for c in range(3, 7)])
    assert MinimaxBot().choose_move(state) in (Move(7, 2), Move(7, 7))


def test_bloquea_un_tres_abierto_del_rival(jugar):
    state = GameState()
    jugar(state, [(14, 0), (14, 4), (14, 8)], [(7, 4), (7, 5), (7, 6)])
    assert MinimaxBot().choose_move(state) in (Move(7, 3), Move(7, 7))


def test_no_modifica_el_estado_recibido(jugar):
    state = GameState()
    jugar(state, [(7, 7), (8, 8)], [(7, 8)])
    copia = state.copy()
    MinimaxBot().choose_move(state)
    assert state.move_count == copia.move_count
    assert all(
        state.cell(r, c) is copia.cell(r, c) for r in range(state.size) for c in range(state.size)
    )


def test_funciona_con_profundidad_uno(jugar):
    state = GameState()
    jugar(state, [(7, 7)], [(7, 8)])
    move = MinimaxBot(depth=1).choose_move(state)
    assert state.is_legal(move)


def test_gana_a_random():
    assert play_match(MinimaxBot(), RandomBot(0)).winner is Player.BLACK
    assert play_match(RandomBot(1), MinimaxBot()).winner is Player.WHITE