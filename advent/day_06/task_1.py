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

logger = logging.getLogger(__name__)


@dataclass
class Race:
    time: int
    record_distance: int


def parse_races(lines: Iterator[str]) -> Iterable[Race]:
    line = next(lines)
    assert line.startswith("Time:")
    times = map(int, line.removeprefix("Time:").strip().split())
    line = next(lines)
    assert line.startswith("Distance:")
    record_distances = map(int, line.removeprefix("Distance:").strip().split())
    for time, record_distance in zip(times, record_distances):
        yield Race(time=time, record_distance=record_distance)


def get_number_of_better_results(race: Race) -> int:
    press_times = np.arange(race.time)
    distances = press_times * (race.time - press_times)
    condition = distances > race.record_distance
    return np.count_nonzero(condition)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    races = parse_races(iter(lines))
    numbers_of_better_solutions = map(get_number_of_better_results, races)
    factor = reduce(operator.mul, numbers_of_better_solutions)
    return str(factor)


if __name__ == "__main__":
    setup_logging()
    main()
