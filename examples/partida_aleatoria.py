"""Partida completa entre dos jugadores aleatorios, sin interfaz."""

import random

from cincoenraya import GameState


def main(seed: int | None = None) -> None:
    rng = random.Random(seed)
    state = GameState()

    while not state.is_over():
        move = rng.choice(state.legal_moves())
        state.play(move)

    print(state)
    print()
    if state.is_draw():
        print(f"Empate tras {state.move_count} movimientos.")
    else:
        print(f"Gana {state.winner.name} tras {state.move_count} movimientos.")


if __name__ == "__main__":
    main()