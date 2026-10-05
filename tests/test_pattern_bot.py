from cincoenraya import GameState, Move, Player, play_match
from cincoenraya.bots import PatternBot, RandomBot

BLANCAS_SUELTAS = [(0, 0), (0, 2), (0, 4), (0, 6)]
NEGRAS_SUELTAS = [(14, 0), (14, 2), (14, 4), (14, 6)]


def test_primer_movimiento_en_el_centro():
    assert PatternBot().choose_move(GameState()) == Move(7, 7)


def test_gana_cuando_puede(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], BLANCAS_SUELTAS)
    assert PatternBot().choose_move(state) in (Move(7, 2), Move(7, 7))


def test_bloquea_cuando_el_rival_va_a_ganar(jugar):
    state = GameState()
    jugar(state, NEGRAS_SUELTAS, [(7, c) for c in range(3, 7)])
    assert PatternBot().choose_move(state) in (Move(7, 2), Move(7, 7))


def test_bloquea_aunque_pudiera_hacer_cuatro(jugar):
    state = GameState()
    jugar(state, [(9, 3), (9, 4), (9, 5), (14, 14)], [(7, c) for c in range(3, 7)])
    assert PatternBot().choose_move(state) in (Move(7, 2), Move(7, 7))


def test_gana_a_random():
    victorias = 0
    for seed in range(4):
        if seed % 2 == 0:
            result = play_match(PatternBot(seed), RandomBot(seed))
            victorias += result.winner is Player.BLACK
        else:
            result = play_match(RandomBot(seed), PatternBot(seed))
            victorias += result.winner is Player.WHITE
    assert victorias >= 3