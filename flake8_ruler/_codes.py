from typing import TYPE_CHECKING, Iterator, Set, Tuple
import flake8_codes
if TYPE_CHECKING:
    from ._config import Config


def get_codes(config: 'Config') -> Iterator[Tuple[str, str]]:
    checked: Set[str] = set()
    for plugin in flake8_codes.get_installed():
        if plugin.name in checked:
            continue
        checked.add(plugin.name)
        rules = config.get_rules(plugin.name)
        try:
            codes = flake8_codes.extract(plugin.name)
        except ImportError:
            continue
        for code, message in codes.items():
            if rules.included(code):
                yield (code, message)
