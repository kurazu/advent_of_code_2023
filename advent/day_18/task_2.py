from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Iterable, NamedTuple

import cv2
import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Direction, Instruction, parse_instruction

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


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    instructions = map(parse_instruction, lines)
    instructions = map(decode_instruction, instructions)
    for instruction in instructions:
        logger.debug("Instruction: %s", instruction)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
