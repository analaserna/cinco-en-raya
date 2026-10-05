"""Descubrimiento automático de los bots del proyecto."""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from cincoenraya import bots as bots_package
from cincoenraya.bot import Bot


def _is_bot_class(obj: object, module_name: str) -> bool:
    """Indica si obj es una clase de bot concreta definida en el módulo indicado.

    issubclass puede lanzar TypeError con objetos que parecen clases pero no
    lo son, como los alias de tipos genéricos (por ejemplo tuple[int, int])
    en Python 3.10. En ese caso se considera que no es un bot.
    """
    try:
        return (
            issubclass(obj, Bot)
            and obj is not Bot
            and obj.__module__ == module_name
            and not inspect.isabstract(obj)
        )
    except TypeError:
        return False


def available_bots() -> dict[str, type[Bot]]:
    """Devuelve todas las clases de bot definidas en cincoenraya.bots.

    Recorre cada módulo del subpaquete y recoge las clases que heredan de
    Bot y no son abstractas. Para añadir un bot nuevo basta con crear un
    archivo en cincoenraya/bots/; no hay que registrarlo en ningún otro sitio.

    Returns:
        Diccionario {nombre de la clase: clase}, ordenado alfabéticamente.
    """
    found: dict[str, type[Bot]] = {}
    for module_info in pkgutil.iter_modules(bots_package.__path__):
        module = importlib.import_module(f"{bots_package.__name__}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if _is_bot_class(obj, module.__name__):
                found[obj.__name__] = obj
    return dict(sorted(found.items()))