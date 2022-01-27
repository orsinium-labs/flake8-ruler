# flake8-ruler

CLI tool to generate a [flake8](https://flake8.pycqa.org/en/latest/) (`setup.cfg`) from a nicer, modern, more powerful, [flakehell](https://github.com/life4/flakehell)-inspired (and 100% compatible) config ([pyproject.toml](https://www.python.org/dev/peps/pep-0518/#tool-table)).

Features:

+ [TOML](https://github.com/toml-lang/toml): type-safe, syntax-highlighted, well standartized config format.
+ Powerful per-plugin codes configuration.
+ Glob patterns.
+ Extending and merging multiple configs, shared configurations.
+ Remote configs.

## Getting started

Install:

```bash
python3 -m pip install flake8-ruler
```

Create `pyproject.toml`:

```toml
# you can add in this section any options supported by flake8
[tool.flake8_ruler]
max_line_length = 90

[tool.flake8_ruler.plugins]
# include everything in pyflakes except F401
pyflakes = ["+*", "-F401"]
# enable only codes from S100 to S199
flake8-bandit = ["-*", "+S1??"]
# enable everything that starts from `flake8-`
"flake8-*" = ["+*"]
# explicitly disable a plugin
flake8-docstrings = ["-*"]
```

Convert `pyproject.toml` into `setup.cfg`:

```bash
python3 -m flake8_ruler
```

Done! Now, you can just run `flake8` and it will automatically use the newly generated config.

## Plugins

In `pyproject.toml` you can specify `[tool.flake8_ruler.plugins]` table. It's a key-value of flake8 plugins and associated to them rules.

Key can be exact plugin name or wildcard template. For example `"flake8-commas"` or `"flake8-*"`. The tool will choose the longest match for every plugin if possible. In the previous example, `flake8-commas` will match to the first pattern, `flake8-bandit` and `flake8-bugbear` to the second, and `pycodestyle` will not match to any pattern.

Value is a list of templates for error codes for this plugin. First symbol in every template must be `+` (include) or `-` (exclude). The latest matched pattern wins. For example, `["+*", "-F*", "-E30?", "-E401"]` means "Include everything except all checks that starts with `F`, check from `E301` to `E310`, and `E401`".

## Codes

An error code is added into the generated `setup.cfg` only if the following conditions match:

1. The plugin is installed in the same environment as flake8-ruler.
1. The code is detected by [flake8-codes](https://github.com/orsinium-labs/flake8-codes). If not, please, contribute.
1. The code is enabled in `[tool.flake8_ruler.plugins]`.

Use flake8-codes to find out the supported error codes for a plugin:

```bash
python3 -m pip install flake8-codes
python3 -m flake8_codes
```

## Inheritance

Option `base` allows to specify base config from which you want to inherit this one. It can be path to local config or remote URL. You can specify one path or list of paths as well. For example:

```toml
base = [
    "https://raw.githubusercontent.com/orsinium-labs/flake8-ruler/master/pyproject.toml",
    ".flake8-ruler.toml",
]
max_line_length = 90
```

In this example, flake8-ruler will read remote config, local config (`.flake8-ruler.toml`), and then current config. So, even if `max_line_length` is specified in some of base configs, it will be overwritten by `max_line_length = 90` from the current config.

## Resources

+ [flake8 documentation](https://flake8.pycqa.org/en/latest/).
+ [flake8-codes](https://github.com/orsinium-labs/flake8-codes) - library used to extract the installed plugins and their error codes.
+ [awesome-flake8-extensions](https://github.com/DmytroLitvinov/awesome-flake8-extensions) - list of flake8 plugins.
+ [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide/) - the biggest flake8 plugin.
