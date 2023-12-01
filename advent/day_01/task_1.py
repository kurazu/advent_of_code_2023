import logging
import string
from itertools import starmap
from pathlib import Path
from typing import Tuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


def get_digits(line: str) -> Tuple[int, int]:
    first_digit: int
    for c in line:
        if c in string.digits:
            first_digit = int(c)
            break
    else:
        raise ValueError(f"Could not find digit in {line!r}")
    last_digit: int
    for c in reversed(line):
        if c in string.digits:
            last_digit = int(c)
            break
    else:
        raise ValueError(f"Could not find digit in {line!r}")
    return first_digit, last_digit


def digits_to_number(first_digit: int, last_digit: int) -> int:
    return first_digit * 10 + last_digit


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    digits = map(get_digits, lines)
    number = starmap(digits_to_number, digits)
    return str(sum(number))


if __name__ == "__main__":
    setup_logging()
    main()
