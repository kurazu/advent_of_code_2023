import logging
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Direction(str, Enum):
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class Instruction(NamedTuple):
    direction: Direction
    distance: int
    color: str


def parse_instruction(line: str) -> Instruction:
    dir, dist, color = line.split()
    return Instruction(Direction(dir), int(dist), color[2:-1])


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    instructions = map(parse_instruction, lines)
    for instruction in instructions:
        logger.debug("Instruction %s", instruction)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
