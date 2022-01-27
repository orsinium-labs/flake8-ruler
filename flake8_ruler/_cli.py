from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import List, NoReturn, TextIO
from typing import Iterator, Set, Tuple
import flake8_codes
from ._config import Config
from ._ini import INI


def normalize(name: str) -> str:
    return name.replace('-', '_').lower()


class Command:
    argv: List[str]
    stream: TextIO
    warnings: int = 0

    def __init__(self, argv, stream) -> None:
        self.argv = argv
        self.stream = stream

    def run(self) -> int:
        parser = ArgumentParser()
        parser.add_argument('--input', default=Path('pyproject.toml'), type=Path)
        parser.add_argument('--output', default=Path('setup.cfg'), type=Path)
        args = parser.parse_args(self.argv)
        config = Config.from_path(args.input)
        ini = INI.from_path(args.output)
        ini.set_config(config)

        expected_plugins = {plugin for plugin in config.plugins if '*' not in plugin}
        installed_plugins = set()
        for plugin_name in sorted(self.get_plugins()):
            installed_plugins.add(plugin_name)
            codes_enabled = 0
            for code, message in self.get_codes(plugin_name, config):
                if not codes_enabled:
                    ini.add_plugin_name(plugin_name)
                codes_enabled += 1
                ini.add_code(code, message)
            if codes_enabled:
                self.print(f"enabled {codes_enabled} codes for {plugin_name}")

        ini.save()

        missed_plugins = expected_plugins - installed_plugins
        for plugin_name in missed_plugins:
            self.warn(f'{plugin_name} is expected but not found')
        return self.warnings

    def get_plugins(self) -> Iterator[str]:
        checked: Set[str] = set()
        for plugin in flake8_codes.get_installed():
            if plugin.name in checked:
                continue
            checked.add(plugin.name)
            yield plugin.name

    def get_codes(self, plugin_name: str, config: 'Config') -> Iterator[Tuple[str, str]]:
        rules = config.get_rules(plugin_name)
        try:
            codes = flake8_codes.extract(plugin_name)
        except ImportError:
            if rules.content:
                self.warn(f"cannot extract codes for {plugin_name}")
            return
        for code, message in codes.items():
            if rules.included(code):
                yield (code, message)

    def warn(self, text: str) -> None:
        print('WARNING:', text, file=self.stream)
        self.warnings += 1

    def print(self, text: str) -> None:
        print(text, file=self.stream)


def entrypoint() -> NoReturn:
    cmd = Command(argv=sys.argv[1:], stream=sys.stdout)
    code = cmd.run()
    sys.exit(code)
