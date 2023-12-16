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


def cycle(board: BoardType) -> None:
    drop(board)
    logger.debug("After north:\n%s", visualize_board(board))
    drop(board.T[:, ::-1])
    logger.debug("After west:\n%s", visualize_board(board))
    drop(board[::-1, :])
    logger.debug("After south:\n%s", visualize_board(board))
    drop(board.T[::-1, :])
    logger.debug("After east:\n%s", visualize_board(board))


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse(lines)
    logger.info("Board:\n%s", visualize_board(board))
    memory: dict[str, int] = {
        visualize_board(board): 0,
    }
    round = 0
    while True:
        cycle(board)
        round += 1
        key = visualize_board(board)
        if key in memory:
            logger.info("Found cycle at round %d", round)
            break
        memory[key] = round
        if round % 100 == 0:
            logger.info("Round %d", round)

    # logger.info("Cycle:\n%s", visualize_board(board))
    load = get_load(board)
    return str(load)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
