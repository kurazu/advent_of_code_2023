import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, NamedTuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Symbol(NamedTuple):
    row: int
    column: int
    value: str


class PartNumber(NamedTuple):
    row: int
    start_column: int
    end_column: int
    value: int


@dataclass
class Schematic:
    symbols: set[Symbol]
    part_numbers: set[PartNumber]


def parse(lines: Iterable[str]) -> Schematic:
    symbols: set[Symbol] = set()
    part_numbers: set[PartNumber] = set()
    for row, line in enumerate(lines):
        buf: list[str] = []

        def maybe_materialize_buffer():
            if buf:
                part_numbers.add(
                    PartNumber(
                        row=row,
                        start_column=col - len(buf),
                        end_column=col,
                        value=int("".join(buf)),
                    )
                )
                buf.clear()

        for col, char in enumerate(line):
            if char == ".":
                maybe_materialize_buffer()
            elif char.isdigit():
                buf.append(char)
            else:
                maybe_materialize_buffer()
                symbols.add(Symbol(row=row, column=col, value=char))
        maybe_materialize_buffer()
    return Schematic(symbols=symbols, part_numbers=part_numbers)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    schematics = parse(lines)
    for part_number in sorted(
        schematics.part_numbers, key=lambda x: (x.row, x.start_column)
    ):
        logger.debug("Part %s", part_number)
    for symbol in sorted(schematics.symbols, key=lambda x: (x.row, x.column)):
        logger.debug("Symbol %s", symbol)
    return str(sum([]))


if __name__ == "__main__":
    setup_logging()
    main()
