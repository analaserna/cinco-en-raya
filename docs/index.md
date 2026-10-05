# Cinco en raya

Implementación open-source del juego cinco en raya (Gomoku) para dos jugadores, con una interfaz web para jugar contra bots y una plataforma para que cualquier desarrollador programe y añada su propio bot.

- Jugar online: [https://cinco-en-raya-cunef.streamlit.app](https://NOMBRE.streamlit.app)
- Código fuente: [github.com/analaserna/cinco-en-raya](https://github.com/analaserna/cinco-en-raya)

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone https://github.com/analaserna/cinco-en-raya.git
cd cinco-en-raya
pip install -e .
```

## Uso rápido

```python
from cincoenraya import GameState, Move, play_match
from cincoenraya.bots import GreedyBot, RandomBot

state = GameState()
state.play(Move(7, 7))
print(state)

result = play_match(GreedyBot(), RandomBot())
print(result.winner_name, result.reason.value)
```

## Contenido

- [Reglas](reglas.md): reglas del juego.
- [Tutorial: crea tu bot](tutorial-bot.md): cómo programar un bot y enviarlo al repositorio, de principio a fin.
- [Referencia del API](api.md): documentación de todas las clases y funciones públicas.
- [Clasificación de bots](https://analaserna.github.io/cinco-en-raya/): resultados del torneo entre todos los bots, actualizados automáticamente.