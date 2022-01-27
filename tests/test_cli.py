from pathlib import Path
import subprocess
import sys
from textwrap import dedent

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
        E902,  # %s
        # pyflakes
        F621,  # too many expressions in star-unpacking assignment
        F622,  # two starred expressions in assignment
"""


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
    exp = dedent(OUTPUT_CONFIG).strip().replace('select =', 'select = ')
    assert actual == exp
