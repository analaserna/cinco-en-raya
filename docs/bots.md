# Bots del proyecto

El proyecto incluye cinco bots, de menor a mayor fuerza. Todos heredan de `Bot` y se descubren automáticamente, por lo que aparecen en la interfaz web, en la validación y en el torneo sin registrarlos en ningún sitio.

| Bot | Clase | Idea principal | Jugadas que mira hacia delante |
|---|---|---|---|
| Aleatorio | `RandomBot` | Movimiento legal al azar | Ninguna |
| Centro | `CenterBot` | Casilla libre más cercana al centro | Ninguna |
| Táctico | `GreedyBot` | Gana o bloquea; si no, alarga sus líneas | Una |
| Patrones | `PatternBot` | Mejor jugada según la evaluación por ventanas | Una |
| Minimax | `MinimaxBot` | Amenazas forzadas y minimax con poda alfa-beta | Varias, según el tiempo |

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

Es el bot más fuerte del proyecto. En cada movimiento sigue este orden:

1. **Ganar o bloquear** en una jugada, como los anteriores.
2. **Victoria por cuatros continuos (VCF).** Busca una secuencia de cuatros, cada uno de los cuales el rival está obligado a tapar, que termine en una doble amenaza imposible de bloquear. Como en cada paso el rival solo tiene una respuesta, puede ver victorias a muchas jugadas de distancia en pocos milisegundos.
3. **Defensa frente a una VCF del rival.** Imagina que pasa el turno y comprueba si el rival tendría una VCF. Si es así, solo considera las jugadas que la impiden.
4. **Minimax con poda alfa-beta.** Explora el árbol de jugadas suponiendo que él elige siempre lo mejor para sí y el rival lo peor para él. Las posiciones finales se valoran con la evaluación por ventanas. La poda alfa-beta descarta las ramas que no pueden cambiar la decisión, con el mismo resultado que el minimax completo.

Para responder en menos de un segundo:

- **Profundidad iterativa:** busca a profundidad 1, 2, 3... hasta agotar medio segundo, y juega la mejor jugada de la última búsqueda completa. Cada iteración explora primero la mejor jugada de la anterior, lo que mejora la poda.
- **Ordenación y límite de jugadas:** en cada posición ordena las candidatas por la mejora de la evaluación y explora solo las 10 más prometedoras.
- **Cálculo incremental:** tanto la evaluación como las casillas candidatas se actualizan con cada jugada, sin recalcularlas desde cero.

## Resultados

La clasificación actualizada del torneo entre todos los bots está en la [página de clasificación](https://analaserna.github.io/cinco-en-raya/).

### Partidas contra humanos

| Partida | Jugador | Color del jugador | Ganador |
|---|---|---|---|
| 1 | | Negras | |
| 2 | | Negras | |
| 3 | | Blancas | |
| 4 | | Negras | |
| 5 | | Negras | |
| 6 | | Blancas | |