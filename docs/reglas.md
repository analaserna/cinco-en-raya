# Reglas

- El tablero es cuadrado, de 15x15 casillas por defecto. Se puede configurar otro tamaño, con un mínimo de 5x5.
- Juegan dos jugadores: negras (X) y blancas (O). Las negras mueven siempre en primer lugar.
- En cada turno, el jugador coloca una ficha en cualquier casilla vacía.
- Gana quien forma una línea de cinco o más fichas propias consecutivas en horizontal, vertical o diagonal.
- Si el tablero se llena sin que nadie haya ganado, la partida termina en empate.

## Partidas entre bots

Cuando juega un bot, se aplican además estas reglas:

- El bot recibe una copia del estado, por lo que no puede alterar la partida real.
- Cada movimiento tiene un tiempo límite.
- Un bot que lanza una excepción, supera el tiempo límite o devuelve un movimiento ilegal pierde la partida inmediatamente.