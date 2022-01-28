import pytest

from flake8_ruler._config import Config


@pytest.mark.parametrize('given1, given2, expected', [
    (
        {'pyflakes': ["+*", "-F401"]},
        {'pyflakes': ["+*", "-F402"]},
        {'pyflakes': ["+*", "-F401", "-F402"]},
    ),
    (
        {'pyflakes': ["+*", "-F401", "-F402"]},
        {'pyflakes': ["+*", "-F403", "-F404"]},
        {'pyflakes': ["+*", "-F401", "-F402", "-F403", "-F404"]},
    ),
    (
        {'pyflakes': ["-F401"]},
        {'pyflakes': ["+*", "-F402"]},
        {'pyflakes': ["+*", "-F401", "-F402"]},
    ),
    (
        {},
        {'pyflakes': ["+*"]},
        {'pyflakes': ["+*"]},
    ),
    (
        {'pyflakes': ["+*"]},
        {},
        {'pyflakes': ["+*"]},
    ),
])
def test_merge_plugins(given1, given2, expected):
    c1 = Config.from_mapping(dict(plugins=given1))
    c2 = Config.from_mapping(dict(plugins=given2))
    merged = c1.merge(c2)
    assert merged.plugins == expected
