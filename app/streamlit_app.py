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
.st-key-tablero {
    gap: 0;
    background: #dcb35c;
    padding: 10px;
    border-radius: 8px;
    max-width: 600px;
}
.st-key-tablero div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap;
    gap: 0;
}
.st-key-tablero div[data-testid="stHorizontalBlock"] > div {
    min-width: 0;
    flex: 1 1 0;
}
.st-key-tablero div[data-testid="stElementContainer"],
.st-key-tablero .stButton {
    width: 100% !important;
}
.st-key-tablero button {
    position: relative;
    width: 100% !important;
    min-height: 0;
    aspect-ratio: 1;
    padding: 0;
    border: none;
    border-radius: 0;
    background:
        linear-gradient(#6b4f1d, #6b4f1d) center / 1px 100% no-repeat,
        linear-gradient(#6b4f1d, #6b4f1d) center / 100% 1px no-repeat;
    color: transparent;
}
.st-key-tablero button p {
    font-size: 0;
}
.st-key-tablero button::after {
    content: "";
    position: absolute;
    inset: 8%;
    border-radius: 50%;
}
.st-key-tablero button[data-testid="stBaseButton-primary"]::after {
    background: radial-gradient(circle at 35% 30%, #666, #000 70%);
}
.st-key-tablero button[data-testid="stBaseButton-secondary"]::after {
    background: radial-gradient(circle at 35% 30%, #fff, #ccc 85%);
    box-shadow: 0 0 0 1px #8a8a8a;
}
.st-key-tablero button[data-testid="stBaseButton-tertiary"]:not(:disabled):hover::after {
    background: rgba(0, 0, 0, 0.25);
}
.st-key-tablero button:disabled {
    opacity: 1;
    cursor: default;
}
.st-key-tablero .coord {
    display: flex;
    align-items: center;
    justify-content: center;
    aspect-ratio: 1;
    font-size: 11px;
    font-weight: 600;
    color: #5a4320;
}
.st-key-tablero div[data-testid="stMarkdownContainer"] {
    width: 100%;
    margin-bottom: 0 !important;
}
.st-key-tablero div[data-testid="stMarkdownContainer"] p {
    margin: 0;
}
</style>
"""

CELL_TYPES = {None: "tertiary", Player.BLACK: "primary", Player.WHITE: "secondary"}

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def coord(move: Move) -> str:
    """Nombre de una casilla en notación de tablero, por ejemplo H8."""
    return f"{LETTERS[move.col]}{move.row + 1}"
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
    """Muestra el estado de la partida y la última jugada."""
    human = st.session_state.human
    bot_name = st.session_state.bot.name
    if st.session_state.forfeit:
        st.success(f"**Has ganado.** {st.session_state.forfeit}")
    elif game.winner is human:
        st.success(f"**Has ganado** en {game.move_count} jugadas.")
    elif game.winner is not None:
        st.error(f"**Ha ganado {bot_name}** en {game.move_count} jugadas.")
    elif game.is_draw():
        st.info("**Empate:** el tablero está lleno.")
    else:
        st.markdown(
            f"Juegas con **{PLAYER_NAMES[human].lower()}** {SYMBOLS[human]} "
            f"contra **{bot_name}**. Jugada {game.move_count + 1}: te toca."
        )
    if game.last_move is not None:
        st.caption(f"Última jugada: {coord(game.last_move)}")

def render_board(game: GameState) -> None:
    """Dibuja el tablero con coordenadas, como una cuadrícula de botones.

    Cada casilla usa un tipo de botón según su contenido (vacía, negra o
    blanca) y el CSS dibuja las líneas y las fichas. La última jugada se
    marca con un punto rojo y, al terminar, la línea ganadora con un borde rojo.
    """
    with st.container(key="tablero"):
        header = st.columns(game.size + 1, gap="small")
        for col in range(game.size):
            header[col + 1].markdown(f'<div class="coord">{LETTERS[col]}</div>', unsafe_allow_html=True)
        for row in range(game.size):
            columns = st.columns(game.size + 1, gap="small")
            columns[0].markdown(f'<div class="coord">{row + 1}</div>', unsafe_allow_html=True)
            for col in range(game.size):
                occupant = game.cell(row, col)
                columns[col + 1].button(
                    SYMBOLS[occupant],
                    key=f"cell-{row}-{col}",
                    type=CELL_TYPES[occupant],
                    on_click=on_cell_click,
                    args=(row, col),
                    disabled=occupant is not None or game.is_over(),
                )

    rules = []
    if game.last_move is not None:
        row, col = game.last_move.row, game.last_move.col
        rules.append(
            f".st-key-cell-{row}-{col} button::before {{"
            "content: ''; position: absolute; inset: 40%; border-radius: 50%;"
            "background: #d62828; z-index: 1; }"
        )
    for move in game.winning_line():
        rules.append(
            f".st-key-cell-{move.row}-{move.col} button::after {{"
            "box-shadow: 0 0 0 3px #d62828, 0 0 8px #d62828; }"
        )
    if rules:
        st.markdown(f"<style>{' '.join(rules)}</style>", unsafe_allow_html=True)

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