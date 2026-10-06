# Tutorial: crea tu propio bot

Este tutorial explica, de principio a fin, cómo programar un bot para el cinco en raya y enviarlo al repositorio mediante una pull request. No es necesario modificar el código del juego: basta con añadir un archivo.

## 1. Requisitos previos

- Python 3.10 o superior.
- Git y una cuenta de GitHub.

## 2. Haz un fork y clona el repositorio

1. Entra en [github.com/analaserna/cinco-en-raya](https://github.com/analaserna/cinco-en-raya) y pulsa **Fork** para crear una copia del repositorio en tu cuenta.
2. Clona tu fork y crea una rama para tu bot:

```bash
git clone https://github.com/TU_USUARIO/cinco-en-raya.git
cd cinco-en-raya
git switch -c bot/mi-bot
```

## 3. Prepara el entorno

En macOS y Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

En Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

Si PowerShell no permite ejecutar el script de activación, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

Todos los tests deben pasar antes de empezar.

## 4. Cómo funciona un bot

Un bot es una clase que hereda de `Bot` e implementa un único método:

```python
def choose_move(self, state: GameState) -> Move:
    ...
```

- `state` es una **copia** del estado de la partida. El bot juega con las fichas de `state.current_player` y puede modificar la copia libremente, por ejemplo para simular jugadas, sin afectar a la partida real.
- Debe devolver un `Move(row, col)` legal. Los movimientos legales se obtienen con `state.legal_moves()`.

Métodos y atributos útiles de `GameState`:

| Método o atributo | Descripción |
|---|---|
| `state.size` | Tamaño del tablero. |
| `state.cell(row, col)` | Ficha de la casilla: `Player.BLACK`, `Player.WHITE` o `None`. |
| `state.legal_moves()` | Lista de movimientos legales. |
| `state.current_player` | Jugador al que le toca, es decir, tu bot. |
| `state.copy()` | Copia independiente del estado. |
| `state.play(move)` | Aplica un movimiento. Útil sobre copias para simular jugadas. |
| `state.winner`, `state.is_over()` | Resultado de la partida. |

Consulta la [referencia del API](api.md) para el detalle completo.

## 5. Escribe tu bot

Crea un archivo nuevo en `src/cincoenraya/bots/`, por ejemplo `src/cincoenraya/bots/center_bot.py`:

```python
"""Bot de ejemplo: juega en la casilla libre más cercana al centro."""

from cincoenraya.bot import Bot
from cincoenraya.game import GameState, Move


class CenterBot(Bot):
    """Elige la casilla libre más próxima al centro del tablero."""

    name = "Centro"

    def choose_move(self, state: GameState) -> Move:
        center = (state.size - 1) / 2
        return min(
            state.legal_moves(),
            key=lambda move: (move.row - center) ** 2 + (move.col - center) ** 2,
        )
```

No hace falta registrar el bot en ningún sitio: el proyecto detecta automáticamente todas las clases de `cincoenraya/bots/` que heredan de `Bot`.

## 6. Normas que debe cumplir tu bot

- El nombre de la clase y el atributo `name` deben ser propios y distintos de los de los demás bots.
- Debe poder crearse sin argumentos, por ejemplo `CenterBot()`.
- Debe devolver siempre un movimiento legal, en tableros de cualquier tamaño (mínimo 5x5).
- Debe responder en menos de 1 segundo por movimiento.
- Solo puede usar la biblioteca estándar de Python y el paquete `cincoenraya`.
- No puede acceder a archivos, a la red ni a otros procesos: no se permite importar módulos como `os`, `sys`, `subprocess` o `socket`, ni llamar a `open`, `eval` o `exec`. La validación revisa el código automáticamente.

Un bot que lanza una excepción, supera el tiempo límite o devuelve un movimiento ilegal pierde la partida automáticamente.

## 7. Prueba tu bot

Juega una partida contra otro bot:

```bash
python -c "from cincoenraya import play_match; from cincoenraya.bots import RandomBot; from cincoenraya.bots.center_bot import CenterBot; r = play_match(CenterBot(), RandomBot(0)); print(r.final_state); print(r.winner_name, r.reason.value)"
```

Comprueba que cumple el contrato del API:

```bash
python -m cincoenraya.validation
```

Tu bot debe aparecer como `[OK]`. Si aparece como `[FALLO]`, el informe indica qué falla.

Por último, ejecuta todos los tests, que incluyen la validación automática de tu bot:

```bash
pytest
```

## 8. Envía tu bot

```bash
git add src/cincoenraya/bots/center_bot.py
git commit -m "Añade CenterBot"
git push -u origin bot/mi-bot
```

En GitHub, abre una pull request desde tu fork hacia la rama `main` de `analaserna/cinco-en-raya`. Los tests se ejecutarán automáticamente. Cuando pasen y los mantenedores revisen el código, tu bot se incorporará al proyecto, aparecerá en la interfaz web y participará en el torneo.