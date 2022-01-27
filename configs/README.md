# flake8_ruler configs

This directory contains some `flake8_ruler` configs that you can directly include into your own using the `base` directive.

Add it in your `pyproject.toml` like this:

```toml
[tool.flake8_ruler]
base = [
    "https://raw.githubusercontent.com/orsinium-labs/flake8-ruler/master/configs/bugs.toml"
]
```
