import itertools as it
import logging
from pathlib import Path
from typing import NamedTuple

import more_itertools as mit

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Shape(NamedTuple):
    z: int | slice
    y: int | slice
    x: int | slice


def parse_shape(line: str) -> Shape:
    start_part, end_part = line.split("~")
    # Z,Y,X
    start_z, start_y, start_x = map(int, reversed(start_part.split(",")))
    end_z, end_y, end_x = map(int, reversed(end_part.split(",")))
    if start_z != end_z:
        assert start_y == end_y
        assert start_x == end_x
        return Shape(slice(start_z, end_z + 1), start_y, start_x)
    elif start_y != end_y:
        assert start_x == end_x
        return Shape(start_z, slice(start_y, end_y + 1), start_x)
    else:
        assert start_x != end_x
        return Shape(start_z, start_y, slice(start_x, end_x + 1))


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    shapes = map(parse_shape, lines)
    for shape in shapes:
        logger.debug("Shape: %s", shape)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
