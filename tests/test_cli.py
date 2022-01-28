import re
import subprocess
import sys
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Tuple

from flake8_ruler import main


INPUT_CONFIG = """
    [tool.flake8_ruler]
    max_line_length = 90

    [tool.flake8_ruler.plugins]
    pyflakes = ["-*", "+F62*"]
"""

OUTPUT_CONFIG = """
    [flake8]
    max_line_length = 90
    select =
        # pycodestyle
        E902,  # *s
        # pyflakes
        F621,  # too many expressions in star-unpacking assignment
        F622,  # two starred expressions in assignment
    ignore =
        C90,  # mccabe
        E,  # pycodestyle
        W,  # pycodestyle
        F,  # pyflakes
"""


def run(*args) -> Tuple[int, str]:
    stream = StringIO()
    code = main(argv=[str(arg) for arg in args], stream=stream)
    stream.seek(0)
    return code, stream.read()


def test_main(tmp_path: Path):
    input_path = tmp_path / 'pyproject.toml'
    output_path = tmp_path / 'setup.cfg'
    input_path.write_text(dedent(INPUT_CONFIG))
    cmd = [
        sys.executable,
        '-m', 'flake8_ruler',
        '--input', str(input_path),
        '--output', str(output_path),
    ]
    result = subprocess.run(cmd)
    assert result.returncode == 0
    actual = output_path.read_text().replace('\t', '    ').strip()
    exp = dedent(OUTPUT_CONFIG).strip()
    exp = exp.replace('select =', 'select = ')
    exp = exp.replace('ignore =', 'ignore = ')
    assert actual == exp


def test_warn_unknown_rule(tmp_path: Path):
    input_path = tmp_path / 'pyproject.toml'
    output_path = tmp_path / 'setup.cfg'
    input_path.write_text(dedent("""
        [tool.flake8_ruler.plugins]
        unknown_plugin = ["+*"]
    """))
    code, output = run('--input', input_path, '--output', output_path)
    assert code == 1
    exp = re.compile('.*unknown_plugin.*expected but not installed')
    assert exp.search(output)
