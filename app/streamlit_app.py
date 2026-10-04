"""Interfaz web del cinco en raya."""

import streamlit as st

from cincoenraya import GameState, play_match
from cincoenraya.bots import GreedyBot, RandomBot

st.set_page_config(page_title="Cinco en raya", layout="centered")

st.title("Cinco en raya")
st.write(
    "Juego por turnos para dos jugadores. Gana quien consiga cinco o más "
    "fichas seguidas en horizontal, vertical o diagonal."
)

st.subheader("Partida de demostración")
st.write("Pulsa el botón para ver una partida completa entre el bot táctico y el bot aleatorio.")

if st.button("Jugar partida de demostración"):
    result = play_match(GreedyBot(), RandomBot())
    st.code(str(result.final_state))
    if result.winner is None:
        st.info(f"Empate tras {len(result.moves)} movimientos.")
    else:
        st.success(
            f"Gana {result.winner_name} ({result.reason.value}) "
            f"tras {len(result.moves)} movimientos."
        )
else:
    st.code(str(GameState()))