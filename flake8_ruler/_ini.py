from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING, List, NamedTuple

if TYPE_CHECKING:
    from ._config import Config


# flakehell fields that aren't supported by flake8
CUSTOM = frozenset({
    'plugins', 'exceptions', 'base',
})


class INI(NamedTuple):
    path: Path
    parser: ConfigParser
    codes: List[str]

    @classmethod
    def from_path(cls, path: Path) -> 'INI':
        ini = INI(
            path=path,
            parser=ConfigParser(interpolation=None),
            codes=[],
        )
        ini.parser.read(str(path))
        return ini

    def set_config(self, config: 'Config') -> None:
        self.parser['flake8'] = {}
        for k, v in config.content.items():
            if k not in CUSTOM:
                self.parser['flake8'][k] = str(v)
        self.parser['flake8']['select'] = ''

    def add_plugin_name(self, plugin_name: str) -> None:
        self.parser['flake8']['select'] += f'\n# {plugin_name}'

    def add_code(self, code: str, message: str) -> None:
        message = message.replace("%", "*")
        self.parser['flake8']['select'] += f'\n{code},  # {message}'

    def save(self) -> None:
        with self.path.open('w') as stream:
            self.parser.write(stream)
