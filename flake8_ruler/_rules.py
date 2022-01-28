from typing import List, NamedTuple

from flake8.utils import fnmatch


class Rules(NamedTuple):
    content: List[str]

    def included(self, code: str) -> bool:
        """
        0. Validate rules

        1. Return True if rule explicitly included
        2. Return False if rule explicitly excluded

        3. Return True if the latest glob-matching rule is include
        4. Return False if the latest glob-matching rule is exclude
        """
        # always report exceptions in file processing
        if code in ('E902', 'E999'):
            return True

        for rule in self.content:
            if len(rule) < 2 or rule[0] not in {'-', '+'}:
                raise ValueError('invalid rule: `{}`'.format(rule))

        for rule in reversed(self.content):
            if code.lower() == rule[1:].lower():
                return rule[0] == '+'

        include = False
        for rule in self.content:
            if fnmatch(code, patterns=[rule[1:]]):
                include = rule[0] == '+'
        return include
