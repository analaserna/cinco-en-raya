import pytest

from cincoenraya.registry import _is_bot_class, available_bots
from cincoenraya.validation import validate_bot

BOTS = available_bots()


def test_se_descubren_los_bots_del_proyecto():
    assert {"GreedyBot", "RandomBot"} <= set(BOTS)


def test_los_nombres_de_los_bots_son_unicos():
    names = [bot_cls().name for bot_cls in BOTS.values()]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("bot_cls", list(BOTS.values()), ids=list(BOTS.keys()))
def test_bot_cumple_el_contrato(bot_cls):
    problems = validate_bot(bot_cls)
    assert problems == [], "\n".join(problems)
    


def test_el_descubrimiento_ignora_objetos_que_no_son_clases_de_bot():
    assert not _is_bot_class(tuple[int, int], "cualquier.modulo")
    assert not _is_bot_class(int, "builtins")