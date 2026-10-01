# Cinco en raya

Implementación open-source del juego **5 en raya** (Gomoku) para dos jugadores,
con una interfaz web para jugar contra bots y una plataforma para que cualquiera
pueda programar y añadir su propio bot.

Proyecto de la asignatura Inteligencia Artificial (3º MAT, CUNEF Universidad, 2026/2027).

## Reglas


- Juegan dos jugadores por turnos: negras empiezan.
- Gana quien consigue cinco fichas seguidas / cinco o más en horizontal, vertical o diagonal.
- Si el tablero se llena sin ganador, la partida acaba en empate.

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
