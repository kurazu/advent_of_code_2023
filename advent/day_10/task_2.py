from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Iterable

import cv2
import more_itertools as mit
import numpy as np
import numpy.typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Board, Cell, Position, parse_board, traverse_board

logger = logging.getLogger(__name__)


CELL_TO_TILE: dict[Cell, npt.NDArray[np.uint8]] = {
    Cell.EMPTY: np.array(
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.START: np.array(
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.NORTH_SOUTH: np.array(
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.EAST_WEST: np.array(
        [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.NORTH_EAST: np.array(
        [
            [0, 1, 0],
            [0, 1, 1],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.NORTH_WEST: np.array(
        [
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.SOUTH_EAST: np.array(
        [
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    ),
    Cell.SOUTH_WEST: np.array(
        [
            [0, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    ),
}


def draw_history(board: Board, history: Iterable[Position]) -> npt.NDArray[np.uint8]:
    image = np.zeros((board.height * 3, board.width * 3), dtype=np.uint8)
    for point in history:
        row, col = point
        image[row * 3 : (row + 1) * 3, col * 3 : (col + 1) * 3] = CELL_TO_TILE[
            board[point]
        ]
    return image


def find_inside_fields(
    board: Board, grayscale_image: npt.NDArray[np.uint8]
) -> Iterable[Position]:
    for row in range(board.height):
        for col in range(board.width):
            tile = grayscale_image[row * 3 : (row + 1) * 3, col * 3 : (col + 1) * 3]
            if np.count_nonzero(tile) == 0:
                yield Position(row, col)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board:\n%s", board)
    logger.debug("Board size: %dx%d", board.width, board.height)
    starting_point = board.find_starting_point()
    logger.debug("Starting point: %s", starting_point)
    # increase max recursion depth
    sys.setrecursionlimit(board.height * board.width)
    history = traverse_board(board, starting_point)
    image = draw_history(board, history)
    grayscale_image = np.where(image, np.uint8(255), np.uint8(0))
    cv2.floodFill(grayscale_image, None, (0, 0), 127)
    cv2.imshow("image", grayscale_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    inside_fields = find_inside_fields(board, grayscale_image)
    number_of_inside_fields = mit.ilen(inside_fields)

    return str(number_of_inside_fields)


if __name__ == "__main__":
    setup_logging(logging.CRITICAL)
    main()
