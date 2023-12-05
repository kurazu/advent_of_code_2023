import itertools as it
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import more_itertools as mit
from returns.curry import partial
from tqdm import trange

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import apply_maps, parse_map

logger = logging.getLogger(__name__)


def _parse_seeds(line: str) -> Iterable[int]:
    for range_start, range_len in mit.batched(map(int, line.split()), 2):
        yield from trange(range_start, range_start + range_len)


def parse_seeds(lines: Iterable[str]) -> Iterable[int]:
    line = next(lines)
    assert next(lines) == ""
    assert line.startswith("seeds: ")
    _, ids = line.split(": ")
    return _parse_seeds(ids)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    seeds = parse_seeds(lines)
    maps = [
        parse_map("seed-to-soil", lines),
        parse_map("soil-to-fertilizer", lines),
        parse_map("fertilizer-to-water", lines),
        parse_map("water-to-light", lines),
        parse_map("light-to-temperature", lines),
        parse_map("temperature-to-humidity", lines),
        parse_map("humidity-to-location", lines),
    ]
    locations = map(partial(apply_maps, maps), seeds)
    min_location = min(locations)
    return str(min_location)


if __name__ == "__main__":
    setup_logging()
    main()
