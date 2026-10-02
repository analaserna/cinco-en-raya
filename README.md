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

```
cinco-en-raya/
├── src/cincoenraya/   # Lógica del juego
├── tests/             # Tests automáticos
├── pyproject.toml     # Configuración del paquete
├── LICENSE
└── README.md
```

## Enlaces

- Jugar online: *próximamente*
- Documentación: *próximamente*
- Clasificación de bots: *próximamente*

## Autores

- Pablo Valcarce
- Ana Laserna 

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta [LICENSE](LICENSE).
