"""
Entrypoint module, in case you use `python -m databasetools`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from .cli import cli_main

        cli_main.cli()
    else:
        from .cli import interactive_shell

        interactive_shell.run_interactive_shell()
