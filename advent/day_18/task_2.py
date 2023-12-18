from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Iterable, List, NamedTuple

import cv2
import numpy as np
import shapely
import sympy
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import DIRECTION_TO_SHIFT, Direction, Instruction, Point, parse_instruction

logger = logging.getLogger(__name__)
HEX_TO_DIRECTION = {
    "0": Direction.RIGHT,
    "1": Direction.DOWN,
    "2": Direction.LEFT,
    "3": Direction.UP,
}


def decode_instruction(instruction: Instruction) -> Instruction:
    distance = instruction.color[:-1]
    parsed_distance = int(distance, 16)
    direction = HEX_TO_DIRECTION[instruction.color[-1]]
    return Instruction(direction, parsed_distance, instruction.color)


def get_points(instructions: Iterable[Instruction]) -> Iterable[Point]:
    current = Point(0, 0)
    yield current
    for instruction in instructions:
        shift = DIRECTION_TO_SHIFT[instruction.direction]
        current = Point(
            current.y + shift.y * instruction.distance,
            current.x + shift.x * instruction.distance,
        )
        yield current


def get_area_shapely(points: List[Point]) -> float:
    polygon = shapely.Polygon(points)
    area: float = polygon.area
    circumference: float = polygon.length
    return area + circumference / 2 + 1


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    instructions = map(parse_instruction, lines)
    instructions = map(decode_instruction, instructions)
    points = list(get_points(instructions))
    area = get_area_shapely(points)
    return str(int(area))


if __name__ == "__main__":
    setup_logging()
    main()
