import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


def parse_seeds(lines: Iterable[str]) -> set[int]:
    line = next(lines)
    assert next(lines) == ""
    assert line.startswith("seeds: ")
    _, ids = line.split(": ")
    return set(map(int, ids.split()))


@dataclass
class Entry:
    dest_start: int
    source_start: int
    range_len: int


@dataclass
class RangeDict:
    entries: list[Entry]

    def __getitem__(self, source_idx: int) -> int:
        for entry in self.entries:
            if entry.source_start <= source_idx < entry.source_start + entry.range_len:
                return entry.dest_start + source_idx - entry.source_start
        return source_idx


def parse_map(name: str, lines: Iterable[str]) -> RangeDict:
    line = next(lines)
    assert line == f"{name} map:", f"expected {name!r} but got {line!r}"
    entries: list[RangeDict] = []
    for line in lines:
        if not line:
            break
        dest_start, source_start, range_len = map(int, line.split())
        entries.append(Entry(dest_start, source_start, range_len))
    return RangeDict(entries)


def apply_maps(maps: list[RangeDict], idx: int) -> int:
    for m in maps:
        idx = m[idx]
    return idx


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    seeds = parse_seeds(lines)
    logger.debug(f"seeds: {seeds}")
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
