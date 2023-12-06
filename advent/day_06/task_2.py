import logging
import operator
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Race, get_number_of_better_results

logger = logging.getLogger(__name__)


def parse_race(lines: Iterator[str]) -> Iterable[Race]:
    line = next(lines)
    assert line.startswith("Time:")
    time = int("".join(line.removeprefix("Time:").strip().split()))
    line = next(lines)
    assert line.startswith("Distance:")
    record_distance = int("".join(line.removeprefix("Distance:").strip().split()))
    return Race(time=time, record_distance=record_distance)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    race = parse_race(iter(lines))
    numbers_of_better_solutions = get_number_of_better_results(race)
    return str(numbers_of_better_solutions)


if __name__ == "__main__":
    setup_logging()
    main()
