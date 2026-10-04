from cincoenraya import EndReason, GameState, Move, Player, play_match
from cincoenraya.bots import GreedyBot, RandomBot

BLANCAS_SUELTAS = [(0, 0), (0, 2), (0, 4), (0, 6)]
NEGRAS_SUELTAS = [(14, 0), (14, 2), (14, 4), (14, 6)]


def test_primer_movimiento_en_el_centro():
    assert GreedyBot().choose_move(GameState()) == Move(7, 7)


def test_gana_cuando_puede(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], BLANCAS_SUELTAS)
    move = GreedyBot().choose_move(state)
    assert move in (Move(7, 2), Move(7, 7))


def test_bloquea_cuando_el_rival_va_a_ganar(jugar):
    state = GameState()
    jugar(state, NEGRAS_SUELTAS, [(7, c) for c in range(3, 7)])
    move = GreedyBot().choose_move(state)
    assert move in (Move(7, 2), Move(7, 7))


def test_prefiere_ganar_a_bloquear(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], [(9, c) for c in range(3, 7)])
    move = GreedyBot().choose_move(state)
    assert move in (Move(7, 2), Move(7, 7))


def test_juega_cerca_de_las_fichas():
    state = GameState()
    state.play(Move(7, 7))
    move = GreedyBot(seed=0).choose_move(state)
    assert abs(move.row - 7) <= 1 and abs(move.col - 7) <= 1


def test_nunca_juega_ilegal_contra_random():
    for seed in range(5):
        result = play_match(GreedyBot(seed), RandomBot(seed))
        assert result.reason in (EndReason.WIN, EndReason.DRAW)


def test_gana_casi_siempre_a_random():
    victorias = 0
    for seed in range(10):
        if seed % 2 == 0:
            result = play_match(GreedyBot(seed), RandomBot(seed))
            victorias += result.winner is Player.BLACK
        else:
            result = play_match(RandomBot(seed), GreedyBot(seed))
            victorias += result.winner is Player.WHITE
    assert victorias >= 8


def test_partida_entre_dos_bots_tacticos():
    result = play_match(GreedyBot(1), GreedyBot(2))
    assert result.reason in (EndReason.WIN, EndReason.DRAW)