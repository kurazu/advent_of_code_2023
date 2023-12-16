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
    memory: list[str] = [
        visualize_board(board),
    ]
    values: list[BoardType] = [
        board.copy(),
    ]
    # memory: dict[str, int] = {
    #     visualize_board(board): 0,
    # }
    round = 0
    while True:
        cycle(board)
        round += 1
        key = visualize_board(board)
        try:
            index = memory.index(key)
        except ValueError:
            memory.append(key)
            values.append(board.copy())
            continue
        else:
            cycle_offset = index
            cycle_len = round - index
            logger.info(
                "Found cycle len %d at round %d to round %d",
                cycle_len,
                round,
                cycle_offset,
            )
            break

    target_rounds = 1000000000
    target_rounds -= cycle_offset
    target_rounds %= cycle_len
    state = values[cycle_offset + target_rounds]

    # logger.info("Cycle:\n%s", visualize_board(board))
    load = get_load(state)
    return str(load)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
