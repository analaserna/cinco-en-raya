# Bots del proyecto

El proyecto incluye seis bots: cinco desarrollados por el equipo y uno externo, recibido por pull request. Van de menor a mayor complejidad. Todos heredan de `Bot` y se descubren automáticamente, por lo que aparecen en la interfaz web, en la validación y en el torneo sin registrarlos en ningún sitio.

| Bot | Clase | Idea principal | Jugadas que mira hacia delante |
|---|---|---|---|
| Aleatorio | `RandomBot` | Movimiento legal al azar | Ninguna |
| Centro | `CenterBot` | Casilla libre más cercana al centro | Ninguna |
| Táctico | `GreedyBot` | Gana o bloquea; si no, alarga sus líneas | Una |
| Patrones | `PatternBot` | Mejor jugada según la evaluación por ventanas | Una |
| Minimax | `MinimaxBot` | Amenazas forzadas y minimax con poda alfa-beta | Varias, según el tiempo |
| monte_zena | `MonteZenaBot` | Bot externo: negamax con poda alfa-beta, tabla de transposición y amenazas forzadas | Varias, según el tiempo (hasta 12) |

## Aleatorio

Elige un movimiento legal al azar. Sirve como rival de referencia y para probar la plataforma. Admite una semilla para que las partidas sean reproducibles.

## Centro

Es el bot de ejemplo del [tutorial](tutorial-bot.md): juega en la casilla libre más próxima al centro del tablero. Se añadió al proyecto mediante una pull request desde un fork, siguiendo el tutorial paso a paso, para comprobar que el proceso de contribución funciona.

## Táctico

Decide mirando solo el movimiento actual, por orden de prioridad:

1. Si puede formar cinco en línea, lo hace.
2. Si el rival puede formar cinco en línea, le bloquea.
3. Si no, elige la casilla que más alarga sus propias líneas o más corta las del rival, dando el doble de peso al ataque.

Solo considera las casillas vecinas a alguna ficha, porque una ficha aislada casi nunca es útil. Su principal limitación es que no ve amenazas que se preparan en varias jugadas, como un tres abierto del rival.

## Patrones

Introduce la **evaluación por ventanas**, que es la base del bot más fuerte. Una ventana es un grupo de 5 casillas consecutivas en horizontal, vertical o diagonal, es decir, una posible línea ganadora. En un tablero de 15x15 hay 572.

- Una ventana con fichas de un solo jugador suma puntos para él según cuántas tenga: 1, 10, 100 o 10.000 para 1, 2, 3 o 4 fichas.
- Las ventanas del rival restan con los mismos valores.
- Una ventana con fichas de los dos jugadores ya no puede dar la victoria a nadie y vale 0.

Esta evaluación distingue de forma natural las líneas abiertas de las cerradas, porque una línea abierta está en más ventanas libres. Al poner una ficha solo cambian las ventanas que pasan por esa casilla (como mucho 20), por lo que el cambio de la evaluación se calcula de forma incremental, sin recorrer el tablero entero.

El bot gana o bloquea si puede y, si no, elige la casilla que más aumenta la evaluación.

## Minimax

Es el bot de búsqueda desarrollado por el equipo. En cada movimiento sigue este orden:

1. **Ganar o bloquear** en una jugada, como los anteriores.
2. **Victoria por cuatros continuos (VCF).** Busca una secuencia de cuatros, cada uno de los cuales el rival está obligado a tapar, que termine en una doble amenaza imposible de bloquear. Como en cada paso el rival solo tiene una respuesta, puede ver victorias a muchas jugadas de distancia en pocos milisegundos.
3. **Defensa frente a una VCF del rival.** Imagina que pasa el turno y comprueba si el rival tendría una VCF. Si es así, solo considera las jugadas que la impiden.
4. **Minimax con poda alfa-beta.** Explora el árbol de jugadas suponiendo que él elige siempre lo mejor para sí y el rival lo peor para él. Las posiciones finales se valoran con la evaluación por ventanas. La poda alfa-beta descarta las ramas que no pueden cambiar la decisión, con el mismo resultado que el minimax completo.

Para responder en menos de un segundo:

- **Profundidad iterativa:** busca a profundidad 1, 2, 3... hasta agotar medio segundo, y juega la mejor jugada de la última búsqueda completa. Cada iteración explora primero la mejor jugada de la anterior, lo que mejora la poda.
- **Ordenación y límite de jugadas:** en cada posición ordena las candidatas por la mejora de la evaluación y explora solo las 10 más prometedoras.
- **Cálculo incremental:** tanto la evaluación como las casillas candidatas se actualizan con cada jugada, sin recalcularlas desde cero.
## monte_zena

Es un bot externo: lo escribió un compañero de otro equipo y llegó al repositorio mediante pull request (#44 y #45), que se fusionaron en `main`. Pasa la misma validación que los demás. A pesar del nombre, **no usa Monte Carlo**: es un bot de búsqueda como Minimax, y el nombre viene de los nombres de sus autores.

En cada movimiento sigue este orden:

1. **Ganar o tapar:** si puede formar cinco, lo hace; si el rival tiene un cuatro, solo considera las casillas que lo tapan.
2. **VCF y defensa:** reutiliza la búsqueda de victorias por cuatros continuos y la defensa frente a la del rival (`find_vcf` y `with_turn_passed`, de `threats.py`).
3. **Negamax con poda alfa-beta y profundidad iterativa**, hasta 12 jugadas o 0,4 segundos por movimiento. Negamax es la forma compacta de escribir minimax en juegos de suma cero: el valor de una posición para un jugador es el opuesto de su valor para el rival.

Para que la poda sea más eficaz añade:

- **Tabla de transposición:** guarda el valor de las posiciones ya analizadas, identificadas con un hash de Zobrist, para no repetir cálculos si se llega a ellas por otro orden de jugadas.
- **Jugadas killer:** prueba primero las jugadas que ya provocaron una poda a la misma profundidad.
- **Tablero propio** con hacer y deshacer jugadas, en lugar de copiar el estado, y evaluación por ventanas actualizada de forma incremental (reutiliza `WINDOW_SCORES` de `heuristics.py`).

## Resultados

La clasificación actualizada del torneo entre todos los bots está en la [página de clasificación](https://analaserna.github.io/cinco-en-raya/).

