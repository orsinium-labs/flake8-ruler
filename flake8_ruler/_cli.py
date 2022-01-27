# built-in
from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import List, NoReturn, TextIO

# app
from ._config import Config
from ._codes import get_codes, get_plugins
from ._ini import INI


def normalize(name: str) -> str:
    return name.replace('-', '_').lower()


def main(argv: List[str], stream: TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('--input', default=Path('pyproject.toml'), type=Path)
    parser.add_argument('--output', default=Path('setup.cfg'), type=Path)
    args = parser.parse_args(argv)
    config = Config.from_path(args.input)
    ini = INI.from_path(args.output)
    ini.set_config(config)
    for plugin_name in sorted(get_plugins()):
        print(plugin_name, file=stream)
        first_code = True
        for code, message in get_codes(plugin_name, config):
            if first_code:
                ini.add_plugin_name(plugin_name)
                first_code = False
            ini.add_code(code, message)
            print(f'  {code:8} | {message}', file=stream)
    ini.save()
    return 0


def entrypoint() -> NoReturn:
    code = main(argv=sys.argv[1:], stream=sys.stdout)
    sys.exit(code)
