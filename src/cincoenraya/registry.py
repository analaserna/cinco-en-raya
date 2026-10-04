"""Descubrimiento automático de los bots del proyecto."""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from cincoenraya import bots as bots_package
from cincoenraya.bot import Bot


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
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, Bot)
                and cls is not Bot
                and cls.__module__ == module.__name__
                and not inspect.isabstract(cls)
            ):
                found[cls.__name__] = cls
    return dict(sorted(found.items()))