# Cinco en raya

Implementación open-source del juego **5 en raya** (Gomoku) para dos jugadores,
con una interfaz web para jugar contra bots y una plataforma para que cualquiera
pueda programar y añadir su propio bot.

Proyecto de la asignatura Inteligencia Artificial (3º MAT, CUNEF Universidad, 2026/2027).

## Reglas

- Tablero de 15x15 (configurable, mínimo 5x5).
- Juegan negras (X) y blancas (O); empiezan siempre las negras.
- En cada turno, el jugador coloca una ficha en una casilla vacía.
- Gana quien consigue cinco o más fichas seguidas en horizontal, vertical o diagonal.
- Si el tablero se llena sin ganador, la partida termina en empate.

## Uso desde código

```python
from cincoenraya import GameState, Move

state = GameState()
state.play(Move(7, 7))  # negras
state.play(Move(7, 8))  # blancas
print(state)
print(state.is_over(), state.winner)
```

Partida completa entre dos jugadores aleatorios:

```bash
python examples/partida_aleatoria.py
```

## Jugar en la web

La interfaz web está publicada en: [https://NOMBRE.streamlit.app](https://cinco-en-raya-cunef.streamlit.app)

Se juega contra uno de los bots del proyecto. En "Opciones de la partida" se elige el bot rival y el color; las negras mueven siempre primero. Cualquier bot nuevo añadido a cincoenraya/bots/ aparece automáticamente en la lista.

Para ejecutarla en local:

```bash
   pip install -e ".[web]"
   streamlit run app/streamlit_app.py
```
## Instalación

Requiere Python 3.10 o superior.

```bash
git clone https://github.com/analaserna/cinco-en-raya.git
cd cinco-en-raya
python3 -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Ejecutar los tests

```bash
pytest
```

## Estructura del proyecto

cinco-en-raya/
├── .github/           # Workflows de GitHub Actions y plantilla de pull request
├── app/               # Interfaz web (Streamlit)
├── docs/              # Documentación (MkDocs)
├── examples/          # Ejemplos de uso desde código
├── src/cincoenraya/   # Lógica del juego, API de bots, motor de partidas y torneo
│   └── bots/          # Bots incluidos en el proyecto
├── tests/             # Tests automáticos
├── .readthedocs.yaml  # Configuración de ReadTheDocs
├── CONTRIBUTING.md    # Guía para contribuir
├── LICENSE
├── README.md
├── mkdocs.yml         # Configuración de la documentación
├── pyproject.toml     # Configuración del paquete
└── requirements.txt   # Dependencias para el despliegue web

## Enlaces

- Jugar online: https://cinco-en-raya-cunef.streamlit.app
- Documentación: https://cinco-en-raya.readthedocs.io/
- Tutorial para crear un bot: https://cinco-en-raya.readthedocs.io/es/latest/tutorial-bot/
- Clasificación de bots: https://analaserna.github.io/cinco-en-raya/

## Bots incluidos

| Bot | Idea principal |
|---|---|
| Aleatorio | Juega movimientos legales al azar. |
| Centro | Juega en la casilla libre más cercana al centro (bot de ejemplo del tutorial). |
| Táctico | Gana o bloquea en una jugada y, si no, alarga sus líneas. |
| Patrones | Elige la jugada que más mejora la evaluación por ventanas. |
| Minimax | Busca victorias por cuatros continuos y usa minimax con poda alfa-beta y profundidad iterativa. |

La explicación detallada de cada bot está en la documentación.

## Contribuir

Cualquier desarrollador puede añadir su propio bot mediante una pull request. Consulta [CONTRIBUTING.md](CONTRIBUTING.md) y el tutorial de la documentación.

## Autores

- Pablo Valcarce
- Ana Laserna 

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta [LICENSE](LICENSE).
