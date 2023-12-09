import logging
from pathlib import Path
from typing import TypeAlias

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)

History: TypeAlias = npt.NDArray[np.int64]


def parse_history(line: str) -> History:
    return np.array(list(map(int, line.split())), dtype=np.int64)


def find_next_element(history: History) -> int:
    last_elements: list[int] = [history[-1]]
    logger.debug("Finding next element for history: %s", history)
    seq = history
    while np.count_nonzero(seq) > 1:
        seq = np.diff(seq)
        last_elements.append(seq[-1])
        logger.debug("seq: %s", seq)
    logger.debug("last_elements: %s", last_elements)
    result: int = np.sum(last_elements)
    logger.info("result: %s", result)
    return result


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    histories = map(parse_history, lines)
    next_elements = map(find_next_element, histories)
    return str(sum(next_elements))


if __name__ == "__main__":
    setup_logging()
    main()
