from __future__ import annotations

import itertools as it
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import more_itertools as mit

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@dataclass
class Shape:
    horizontal_tiles: set[tuple[int, int]]
    low_z: int
    high_z: int

    def drop(self) -> Shape:
        return Shape(
            horizontal_tiles=self.horizontal_tiles,
            low_z=self.low_z - 1,
            high_z=self.high_z - 1,
        )


def parse_shape(line: str) -> Shape:
    start_part, end_part = line.split("~")
    # Z,Y,X
    start_z, start_y, start_x = map(int, reversed(start_part.split(",")))
    end_z, end_y, end_x = map(int, reversed(end_part.split(",")))
    if start_z != end_z:  # vertical line
        assert start_y == end_y
        assert start_x == end_x
        return Shape(horizontal_tiles={(start_y, start_x)}, low_z=start_z, high_z=end_z)
    elif start_y != end_y:  # horizontal line stretching along y axis
        assert start_x == end_x
        return Shape(
            horizontal_tiles={(y, start_x) for y in range(start_y, end_y + 1)},
            low_z=start_z,
            high_z=start_z,
        )
    else:
        return Shape(
            horizontal_tiles={(start_y, x) for x in range(start_x, end_x + 1)},
            low_z=start_z,
            high_z=start_z,
        )


def drop(shapes: list[Shape]) -> list[Shape]:
    # the shapes are ordered by low_z (the first one in the list
    # is the closest one to the ground).
    settled: list[Shape] = []  # here we will store the shapes that have settled on
    # the ground already
    for falling_shape in shapes:
        while falling_shape.low_z > 1:
            new_low_z = falling_shape.low_z - 1
            # check if dropping the shape by 1 will make it clash with any of the
            # settled shapes
            for settled_shape in settled:
                if settled_shape.high_z < new_low_z:
                    # settled shape is too far away
                    continue
                intersection = settled_shape.horizontal_tiles.intersection(
                    falling_shape.horizontal_tiles
                )
                if intersection:
                    # there is a clash
                    # we need to stop dropping the shape
                    break
                else:
                    # no clashes with settled shape
                    continue
            else:
                # no clashes with any of the settled shapes
                falling_shape = falling_shape.drop()
                continue  # keep falling
            # if we are here, it means that we have found a clash with a settled shape
            # this shape cannot fall any further
            break
        # if we are here, it means that the shape has settled on the ground or on
        # another settled shape
        settled.append(falling_shape)
    return settled


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    shapes = sorted(map(parse_shape, lines), key=lambda s: s.low_z)
    for shape in shapes:
        logger.debug("Shape: %s", shape)
    logger.debug("Dropping shapes")
    shapes = drop(shapes)
    for shape in shapes:
        logger.debug("Shape: %s", shape)

    def can_be_disintegrated(shape: Shape) -> bool:
        shapes_without_this_one = [s for s in shapes if s is not shape]
        dropped = drop(shapes_without_this_one)
        return dropped == shapes_without_this_one

    return str(mit.ilen(filter(can_be_disintegrated, shapes)))


if __name__ == "__main__":
    setup_logging()
    main()
