import sys

verbose = False


def debug(message: str) -> None:
    if verbose:
        print(message, file=sys.stderr)


def info(message: str) -> None:
    print(message, file=sys.stderr)


def error(message: str) -> None:
    print(message, file=sys.stderr)
