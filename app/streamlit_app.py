"""Interfaz web del cinco en raya."""

import streamlit as st

from cincoenraya import GameState, InvalidMoveError, Move, Player, play_match
from cincoenraya.bots import GreedyBot, RandomBot
from cincoenraya.match import BotError, BotTimeoutError, ask_bot
from cincoenraya.registry import available_bots

BOARD_SIZE = 15
BOT_TIME_LIMIT = 2.0
SYMBOLS = {None: "·", Player.BLACK: "●", Player.WHITE: "○"}
PLAYER_NAMES = {Player.BLACK: "Negras", Player.WHITE: "Blancas"}
COLOR_OPTIONS = ["Negras (empiezas tú)", "Blancas (empieza el bot)"]
BOTS = {bot_cls.name: bot_cls for bot_cls in available_bots().values()}
DEFAULT_BOT = GreedyBot.name

BOARD_CSS = """
<style>
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap;
    gap: 2px;
}
div[data-testid="stHorizontalBlock"] > div {
    min-width: 0;
    flex: 1 1 0;
}
div[data-testid="stHorizontalBlock"] button {
    width: 100%;
    min-height: 0;
    padding: 0;
    aspect-ratio: 1;
}
</style>
"""


def new_game(keep_bot: bool = False) -> None:
    """Empieza una partida nueva con las opciones elegidas.

    Si keep_bot es True y ya hay un bot en la sesión, se conserva ese bot
    en lugar de crear el elegido en las opciones. Lo usan los tests.
    """
    if not (keep_bot and "bot" in st.session_state):
        st.session_state.bot = BOTS[st.session_state.get("opt_bot", DEFAULT_BOT)]()
    color = st.session_state.get("opt_color", COLOR_OPTIONS[0])
    st.session_state.human = Player.BLACK if color == COLOR_OPTIONS[0] else Player.WHITE
    st.session_state.game = GameState(BOARD_SIZE)
    st.session_state.error = None
    st.session_state.forfeit = None
    if st.session_state.human is Player.WHITE:
        bot_turn()


def bot_turn() -> None:
    """Pide su movimiento al bot. Si falla, tarda demasiado o juega ilegal, pierde."""
    game = st.session_state.game
    bot = st.session_state.bot
    try:
        game.play(ask_bot(bot, game.copy(), BOT_TIME_LIMIT))
    except BotTimeoutError:
        reason = "tiempo agotado"
    except BotError as exc:
        reason = f"error ({exc})"
    except InvalidMoveError as exc:
        reason = f"movimiento ilegal ({exc})"
    else:
        return
    game.winner = st.session_state.human
    st.session_state.forfeit = f"{bot.name} pierde la partida por {reason}."


def on_cell_click(row: int, col: int) -> None:
    """Juega el movimiento del humano y, si la partida sigue, responde el bot."""
    game = st.session_state.game
    if game.is_over() or game.current_player is not st.session_state.human:
        return
    try:
        game.play(Move(row, col))
    except InvalidMoveError as exc:
        st.session_state.error = str(exc)
        return
    st.session_state.error = None
    if not game.is_over():
        bot_turn()


def render_options() -> None:
    """Opciones de la partida: bot rival y color del humano."""
    with st.expander("Opciones de la partida"):
        names = list(BOTS)
        st.selectbox(
            "Bot rival",
            names,
            index=names.index(DEFAULT_BOT),
            key="opt_bot",
            on_change=new_game,
        )
        st.radio("Juegas con", COLOR_OPTIONS, key="opt_color", on_change=new_game)
        st.caption("Al cambiar una opción empieza una partida nueva. Las negras mueven primero.")


def render_status(game: GameState) -> None:
    """Muestra el estado de la partida."""
    human = st.session_state.human
    bot_name = st.session_state.bot.name
    if st.session_state.forfeit:
        st.success(f"{st.session_state.forfeit} Has ganado.")
    elif game.winner is human:
        st.success("Has ganado.")
    elif game.winner is not None:
        st.error(f"Ha ganado {bot_name}.")
    elif game.is_draw():
        st.info("Empate: el tablero está lleno.")
    else:
        st.write(
            f"Juegas con **{PLAYER_NAMES[human].lower()}** {SYMBOLS[human]} "
            f"contra **{bot_name}**. Te toca."
        )
        if game.last_move is not None:
            st.caption(
                f"Último movimiento del bot: fila {game.last_move.row + 1}, "
                f"columna {game.last_move.col + 1}."
            )


def render_board(game: GameState) -> None:
    """Dibuja el tablero como una cuadrícula de botones."""
    for row in range(game.size):
        columns = st.columns(game.size, gap="small")
        for col, column in enumerate(columns):
            occupant = game.cell(row, col)
            column.button(
                SYMBOLS[occupant],
                key=f"cell-{row}-{col}",
                on_click=on_cell_click,
                args=(row, col),
                disabled=occupant is not None or game.is_over(),
            )


def render_demo() -> None:
    """Partida de demostración entre dos bots."""
    with st.expander("Partida de demostración entre bots"):
        if st.button("Jugar partida de demostración", key="demo"):
            result = play_match(GreedyBot(), RandomBot())
            st.code(str(result.final_state))
            if result.winner is None:
                st.info(f"Empate tras {len(result.moves)} movimientos.")
            else:
                st.success(
                    f"Gana {result.winner_name} ({result.reason.value}) "
                    f"tras {len(result.moves)} movimientos."
                )


st.set_page_config(page_title="Cinco en raya", layout="centered")
st.markdown(BOARD_CSS, unsafe_allow_html=True)

if "game" not in st.session_state:
    new_game(keep_bot=True)

game: GameState = st.session_state.game

st.title("Cinco en raya")
st.caption("Gana quien consiga cinco o más fichas seguidas en horizontal, vertical o diagonal.")

render_options()
render_status(game)
if st.session_state.error:
    st.error(st.session_state.error)

render_board(game)

st.button("Nueva partida", key="nueva-partida", on_click=new_game)

render_demo()