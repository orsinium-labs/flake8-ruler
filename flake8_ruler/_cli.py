from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import List, NoReturn, TextIO, NamedTuple
from typing import Iterator
import flake8_codes
from ._config import Config
from ._ini import INI


def normalize(name: str) -> str:
    return name.replace('-', '_').lower()


RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
END = '\033[0m'


class Code(NamedTuple):
    code: str
    message: str


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

        for plugin in self.get_plugins(config):
            codes_enabled = 0
            for prefix in plugin.codes:
                ini.exclude(prefix, plugin.name)
            for code in self.get_codes(plugin.name, config):
                if not codes_enabled:
                    ini.include_plugin(plugin.name)
                codes_enabled += 1
                ini.include(code.code, code.message)
            if codes_enabled:
                self.print(f"{GREEN}{plugin.name}{END}: {codes_enabled} enabled")
            else:
                self.print(f"{BLUE}{plugin.name}{END}: installed but disabled")
        ini.save()
        return self.warnings

    def get_plugins(self, config: Config) -> Iterator[flake8_codes.Plugin]:
        expected_plugins = {plugin for plugin in config.plugins if '*' not in plugin}
        installed_plugins = set()
        for plugin in sorted(flake8_codes.get_installed()):
            if plugin.name in installed_plugins:
                continue
            installed_plugins.add(plugin.name)
            yield plugin
        missed_plugins = expected_plugins - installed_plugins
        for plugin_name in missed_plugins:
            self.warn(f'{YELLOW}{plugin_name}{END}: expected but not installed')

    def get_codes(self, plugin_name: str, config: 'Config') -> Iterator[Code]:
        rules = config.get_rules(plugin_name)
        try:
            codes = flake8_codes.extract(plugin_name)
        except ImportError:
            if rules.content:
                self.warn(f"{RED}{plugin_name}{END}: cannot extract codes")
            return
        for code, message in codes.items():
            if rules.included(code):
                yield Code(code=code, message=message)

    def warn(self, text: str) -> None:
        print(text, file=self.stream)
        self.warnings += 1

    def print(self, text: str) -> None:
        print(text, file=self.stream)


def main(*, argv: List[str], stream: TextIO) -> int:
    return Command(argv=argv, stream=stream).run()


def entrypoint() -> NoReturn:
    code = main(argv=sys.argv[1:], stream=sys.stdout)
    sys.exit(code)
