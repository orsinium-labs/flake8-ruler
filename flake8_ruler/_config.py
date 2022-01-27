from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, NamedTuple
import re
import toml
import urllib3
from flake8.utils import normalize_paths
from flake8.utils import fnmatch
from ._rules import Rules

REX_NAME = re.compile(r'[-_.]+')
TOOL_NAMES = ('flake8-ruler', 'flake8_ruler', 'flakehell')


class Config(NamedTuple):
    content: Dict[str, Any]

    @property
    def plugins(self) -> Dict[str, List[str]]:
        return self.content['plugins']

    @classmethod
    def from_path(cls, *paths: Union[str, Path]) -> 'Config':
        config = cls({})
        for path in paths:
            if isinstance(path, Path):
                new_config = cls._read_local(path)
            elif path.startswith(('https://', 'http://')):
                new_config = cls._read_remote(path)
            elif Path(path).exists():
                new_config = cls._read_local(Path(path))
            else:
                new_config = cls._read_remote(path)
            config = config.merge(new_config)
        return config

    @classmethod
    def _read_local(cls, path: Path) -> 'Config':
        with path.open('r') as stream:
            return cls.from_content(stream.read())

    @classmethod
    def _read_remote(cls, url: str) -> 'Config':
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return cls.from_content(response.data.decode())

    def merge(self, *other: 'Config') -> 'Config':
        config = self.content.copy()
        for subconfig in other:
            config.update(subconfig.content)

        for section in ('plugins', 'exceptions'):
            config[section] = dict()
            for subconfig in other:
                config[section].update(subconfig.content.get(section, {}))

        return type(self)(config)

    @classmethod
    def from_content(cls, content: str) -> 'Config':
        config = toml.loads(content).get('tool', {})
        for tool_name in TOOL_NAMES:
            if tool_name in config:
                config = config[tool_name]
                break
        config = cls(config)

        for section in ('plugins', 'exceptions'):
            if section in config.content:
                config.content[section] = dict(config.content[section])

        if 'base' in config.content:
            paths = config.content['base']
            if not isinstance(paths, list):
                paths = [paths]
            config = config.merge(cls.from_path(*paths), config)

        if 'exclude' in config.content:
            config.content['exclude'] = normalize_paths(config.content['exclude'])

        return config

    def get_rules(self, plugin_name: str) -> Rules:
        """Get rules for plugin from `plugins` in the config

        Plugin name can be specified as a glob expression.
        So, it's not trivial to match the right one

        1. Try to find exact match (normalizing as all packages names normalized)
        2. Try to find globs that match and select the longest one (nginx-style)
        3. Return empty list if nothing is found.
        """
        if not self.plugins:
            return Rules([])
        plugin_name = REX_NAME.sub('-', plugin_name).lower()
        # try to find exact match
        for pattern, rules in self.plugins.items():
            if '*' not in pattern and REX_NAME.sub('-', pattern).lower() == plugin_name:
                return Rules(rules)

        # try to find match by pattern and select the longest
        best_match: Tuple[int, List[str]] = (0, [])
        for pattern, rules in self.plugins.items():
            if not fnmatch(filename=plugin_name, patterns=[pattern]):
                continue
            match = len(pattern)
            if match > best_match[0]:
                best_match = match, rules
        if best_match[0]:
            return Rules(best_match[1])

        return Rules([])
