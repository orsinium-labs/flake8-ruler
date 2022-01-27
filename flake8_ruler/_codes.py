from typing import TYPE_CHECKING, Iterator, Set, Tuple
import flake8_codes
if TYPE_CHECKING:
    from ._config import Config


def get_plugins() -> Iterator[str]:
    checked: Set[str] = set()
    for plugin in flake8_codes.get_installed():
        if plugin.name in checked:
            continue
        checked.add(plugin.name)
        yield plugin.name


def get_codes(plugin_name: str, config: 'Config') -> Iterator[Tuple[str, str]]:
    rules = config.get_rules(plugin_name)
    try:
        codes = flake8_codes.extract(plugin_name)
    except ImportError:
        return
    for code, message in codes.items():
        if rules.included(code):
            yield (code, message)
