from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import numpy as np
from numpy import typing as npt
from typing_extensions import TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import MAP, BoardType, drop, get_load, parse

logger = logging.getLogger(__name__)


def visualize_board(board: BoardType) -> str:
    inverse_map = {v: k for k, v in MAP.items()}
    return "\n".join("".join(inverse_map[c] for c in row) for row in board)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse(lines)
    logger.debug("Board:\n%s", visualize_board(board))
    drop(board)
    logger.debug("Dropped:\n%s", visualize_board(board))
    load = get_load(board)
    return str(load)


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
