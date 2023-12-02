import logging
from itertools import starmap
from pathlib import Path
from typing import Tuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import digits_to_number

logger = logging.getLogger(__name__)

numbers = r"one|two|three|four|five|six|seven|eight|nine"
digits = r"1|2|3|4|5|6|7|8|9"

targets = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}


def get_digits(line: str) -> Tuple[int, int]:
    first_digit: int
    for i in range(len(line)):
        for key, value in targets.items():
            if line[i:].startswith(key):
                first_digit = value
                break
        else:
            continue
        break
    else:
        raise ValueError(f"Could not find digit in {line!r}")

    last_digit: int
    for i in range(len(line), 0, -1):
        for key, value in targets.items():
            if line[:i].endswith(key):
                last_digit = value
                break
        else:
            continue
        break
    else:
        raise ValueError(f"Could not find digit in {line!r}")

    logger.debug("In line %r, found digits %r and %r", line, first_digit, last_digit)
    return first_digit, last_digit


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    digits = map(get_digits, lines)
    number = starmap(digits_to_number, digits)
    return str(sum(number))


if __name__ == "__main__":
    setup_logging()
    main()
