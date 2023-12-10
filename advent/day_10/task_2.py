from __future__ import annotations

import logging
import math
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, NamedTuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import parse_board, traverse_board

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board:\n%s", board)
    starting_point = board.find_starting_point()
    logger.debug("Starting point: %s", starting_point)
    return ""
    # increase max recursion depth
    sys.setrecursionlimit(board.height * board.width)
    history = traverse_board(board, starting_point)
    logger.debug("History: %s (len %d)", format_history(board, history), len(history))
    return str(math.ceil(len(history) / 2))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
