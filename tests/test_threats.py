from cincoenraya import GameState, Move, Player
from cincoenraya.bots.threats import find_vcf, threats_after, winning_cells, with_turn_passed

BLANCAS_LEJOS = [(0, 0), (0, 7), (0, 14)]


def test_detecta_cinco_en_linea(jugar):
    state = GameState()
    jugar(state, [(7, c) for c in range(3, 7)], BLANCAS_LEJOS + [(14, 14)])
    wins, _ = threats_after(state, Move(7, 7), Player.BLACK)
    assert wins


def test_detecta_la_casilla_de_un_cuatro_cerrado(jugar):
    state = GameState()
    jugar(state, [(5, 3), (5, 4), (5, 5)], [(5, 2), (0, 14), (14, 14)])
    assert threats_after(state, Move(5, 6), Player.BLACK) == (False, {(5, 7)})


def test_un_cuatro_abierto_da_dos_casillas(jugar):
    state = GameState()
    jugar(state, [(7, 4), (7, 5), (7, 6)], BLANCAS_LEJOS)
    assert threats_after(state, Move(7, 3), Player.BLACK) == (False, {(7, 2), (7, 7)})


def test_casillas_ganadoras(jugar):
    state = GameState()
    jugar(state, [(7, 4), (7, 5), (7, 6), (14, 14)], [(0, 0), (0, 1), (0, 2), (0, 3)])
    assert winning_cells(state, Player.WHITE) == {(0, 4)}
    assert winning_cells(state, Player.BLACK) == set()


def test_vcf_inmediata_con_un_tres_abierto(jugar):
    state = GameState()
    jugar(state, [(7, 4), (7, 5), (7, 6)], BLANCAS_LEJOS)
    assert find_vcf(state) in (Move(7, 3), Move(7, 7))


def test_vcf_en_dos_pasos(jugar):
    state = GameState()
    negras = [(5, 3), (5, 4), (5, 5), (6, 6), (7, 6)]
    blancas = [(5, 2), (0, 0), (0, 14), (14, 0), (14, 14)]
    jugar(state, negras, blancas)
    assert find_vcf(state) == Move(5, 6)


def test_sin_vcf_en_una_posicion_tranquila(jugar):
    state = GameState()
    jugar(state, [(7, 7)], [(7, 8)])
    assert find_vcf(state) is None


def test_no_hay_vcf_si_el_rival_tiene_un_cuatro(jugar):
    state = GameState()
    jugar(state, [(7, 4), (7, 5), (7, 6), (14, 14)], [(0, 0), (0, 1), (0, 2), (0, 3)])
    assert find_vcf(state) is None


def test_pasar_el_turno():
    state = GameState()
    state.play(Move(7, 7))
    passed = with_turn_passed(state)
    assert passed.current_player is Player.BLACK
    assert state.current_player is Player.WHITE