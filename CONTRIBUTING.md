# Cómo contribuir

Gracias por tu interés en contribuir a este proyecto. La contribución más habitual es añadir un bot nuevo, pero también son bienvenidas las correcciones de errores y las mejoras del juego, la web o la documentación.

## Añadir un bot

El proceso completo está explicado paso a paso en el [tutorial de la documentación](https://cinco-en-raya.readthedocs.io/en/latest/tutorial-bot/). En resumen:

1. Haz un fork del repositorio y crea una rama.
2. Añade un archivo con tu bot en `src/cincoenraya/bots/`. No hace falta registrarlo en ningún otro sitio.
3. Comprueba que tu bot es válido y que todos los tests pasan:

```bash
   python -m cincoenraya.validation
   pytest
```

4. Abre una pull request desde tu fork hacia la rama `main` de este repositorio y completa la plantilla.

### Normas para los bots

- El nombre de la clase y el atributo `name` deben ser propios y distintos de los de los demás bots.
- El bot debe poder crearse sin argumentos.
- Debe devolver siempre un movimiento legal, en tableros de cualquier tamaño (mínimo 5x5), en menos de 1 segundo por movimiento.
- Solo puede usar la biblioteca estándar de Python y el paquete `cincoenraya`.
- No puede acceder a archivos, a la red ni a otros procesos: no se permite importar módulos como `os`, `sys`, `subprocess` o `socket`, ni llamar a `open`, `eval` o `exec`.

La validación comprueba automáticamente todas estas normas.

## Revisión de las pull requests

Cada pull request pasa por dos revisiones:

1. **Automática.** GitHub Actions ejecuta todos los tests en Python 3.10, 3.11 y 3.12, incluida la validación de todos los bots y la revisión de seguridad de su código, y comprueba que la documentación se genera sin errores. Si algún check falla, la pull request no se puede fusionar.
2. **Manual.** Un mantenedor revisa el código: que el bot hace lo que describe, que es comprensible y que solo añade archivos en `src/cincoenraya/bots/`.

Si es tu primera contribución, GitHub pedirá a un mantenedor que apruebe la ejecución de los tests antes de que empiecen. Una vez fusionada la pull request, tu bot aparecerá automáticamente en la interfaz web y participará en el torneo.

## Otras contribuciones

Para informar de un error o proponer una mejora, abre un issue describiendo el problema y, si es posible, cómo reproducirlo. Las pull requests con cambios en el juego deben incluir tests y mantener los docstrings actualizados, ya que la referencia del API se genera a partir de ellos.