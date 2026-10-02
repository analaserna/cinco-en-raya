import pytest

from cincoenraya import Bot, GameState, Move, Player
from cincoenraya.bots import RandomBot


def test_bot_es_abstracto():
    with pytest.raises(TypeError):
        Bot()


def test_subclase_sin_choose_move_no_se_puede_crear():
    class BotIncompleto(Bot):
        pass

    with pytest.raises(TypeError):
        BotIncompleto()


def test_subclase_minima_funciona():
    class PrimeraCasilla(Bot):
        name = "Primera casilla"

        def choose_move(self, state):
            return state.legal_moves()[0]

    bot = PrimeraCasilla()
    assert bot.choose_move(GameState()) == Move(0, 0)
    assert str(bot) == "Primera casilla"


def test_nombre_por_defecto():
    class SinNombre(Bot):
        def choose_move(self, state):
            return state.legal_moves()[0]

    assert SinNombre().name == "Bot sin nombre"


def test_random_bot_siempre_devuelve_movimientos_legales():
    state = GameState()
    bot = RandomBot(seed=0)
    while not state.is_over():
        move = bot.choose_move(state)
        assert state.is_legal(move)
        state.play(move)


def test_random_bot_con_semilla_es_reproducible():
    state = GameState()
    assert RandomBot(seed=42).choose_move(state) == RandomBot(seed=42).choose_move(state)


@pytest.mark.parametrize("seed", range(10))
def test_partida_entre_dos_random_bots(seed):
    state = GameState()
    bots = {Player.BLACK: RandomBot(seed), Player.WHITE: RandomBot(seed + 100)}
    while not state.is_over():
        bot = bots[state.current_player]
        state.play(bot.choose_move(state.copy()))
    assert state.winner is not None or state.is_draw()
    