import sys


def info(message: str) -> None:
    print(message, file=sys.stderr)


def error(message: str) -> None:
    print(message, file=sys.stderr)
