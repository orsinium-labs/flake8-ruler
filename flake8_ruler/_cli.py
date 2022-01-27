# built-in
from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import Iterator, List, NamedTuple, NoReturn, TextIO

# app
from ._config import Config
from ._codes import get_codes


TEMPLATE = '{code:8} | {message}'


def normalize(name: str) -> str:
    return name.replace('-', '_').lower()


def main(argv: List[str], stream: TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('--config', default=Path('pyproject.toml'), type=Path)
    args = parser.parse_args(argv)
    config = Config.from_path(args.config)
    for code, message in get_codes(config):
        print(TEMPLATE.format(code=code, message=message), file=stream)
    return 0


def entrypoint() -> NoReturn:
    code = main(argv=sys.argv[1:], stream=sys.stdout)
    sys.exit(code)
