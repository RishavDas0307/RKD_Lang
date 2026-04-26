#!/usr/bin/env python3
"""
RKD_Lang — entry point.

Usage:
  python -m rkd              # start REPL
  python -m rkd file.rkd    # run a file
"""

import sys
from .lexer     import Lexer, LexError
from .parser    import Parser, ParseError
from .evaluator import Evaluator, RKDError, make_stdlib


def run_source(source: str, env, show_result: bool = False):
    """Lex → parse → eval a source string. Returns the final value."""
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    result = Evaluator().eval(ast, env)
    if show_result and result is not None:
        ev = Evaluator()
        print(ev._display(result))
    return result


def run_file(path: str):
    try:
        source = open(path).read()
    except FileNotFoundError:
        print(f"Error: file not found: {path!r}")
        sys.exit(1)

    env = make_stdlib()
    try:
        run_source(source, env)
    except (LexError, ParseError, RKDError) as e:
        print(e)
        sys.exit(1)


BANNER = """\
╔══════════════════════════════════════╗
║   RKD_Lang  v0.1   — type 'exit'    ║
╚══════════════════════════════════════╝
"""

HELP = """
Commands:
  exit / quit    Exit the REPL
  :env           Show all variables in scope
  :help          Show this message
"""


def repl():
    print(BANNER)
    env = make_stdlib()
    ev  = Evaluator()

    while True:
        try:
            line = input("rkd> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue
        if line in ("exit", "quit"):
            print("Bye!")
            break
        if line == ":help":
            print(HELP)
            continue
        if line == ":env":
            for k, v in env.store.items():
                print(f"  {k} = {ev._display(v)}")
            continue

        try:
            result = run_source(line, env, show_result=True)
        except (LexError, ParseError, RKDError) as e:
            print(f"  ! {e}")


def main():
    if len(sys.argv) == 1:
        repl()
    else:
        run_file(sys.argv[1])


if __name__ == "__main__":
    main()