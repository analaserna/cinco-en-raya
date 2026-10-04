"""Interfaz web del cinco en raya."""

import streamlit as st

from cincoenraya import GameState, InvalidMoveError, Move, Player, play_match
from cincoenraya.bots import GreedyBot, RandomBot

BOARD_SIZE = 15
SYMBOLS = {None: "·", Player.BLACK: "●", Player.WHITE: "○"}
PLAYER_NAMES = {Player.BLACK: "Negras", Player.WHITE: "Blancas"}

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


def new_game() -> None:
    """Empieza una partida nueva."""
    st.session_state.game = GameState(BOARD_SIZE)
    st.session_state.error = None


def on_cell_click(row: int, col: int) -> None:
    """Juega en la casilla pulsada."""
    try:
        st.session_state.game.play(Move(row, col))
        st.session_state.error = None
    except InvalidMoveError as exc:
        st.session_state.error = str(exc)


def render_status(game: GameState) -> None:
    """Muestra de quién es el turno o cómo ha terminado la partida."""
    if game.winner is not None:
        st.success(f"Ganan las {PLAYER_NAMES[game.winner].lower()}.")
    elif game.is_draw():
        st.info("Empate: el tablero está lleno.")
    else:
        player = game.current_player
        st.write(f"Turno de: **{PLAYER_NAMES[player]}** {SYMBOLS[player]}")


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
    new_game()

game: GameState = st.session_state.game

st.title("Cinco en raya")
st.caption("Gana quien consiga cinco o más fichas seguidas en horizontal, vertical o diagonal.")

render_status(game)
if st.session_state.error:
    st.error(st.session_state.error)

render_board(game)

st.button("Nueva partida", key="nueva-partida", on_click=new_game)

render_demo()