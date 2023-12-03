import logging
from pathlib import Path
from typing import Sequence

from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import PartNumber, Symbol, is_adjacent, parse

logger = logging.getLogger(__name__)


def get_adjacent_part_numbers(
    part_numbers: Sequence[PartNumber], symbol: Symbol
) -> tuple[Symbol, set[PartNumber]]:
    adjacent_part_numbers: set[PartNumber] = {
        part_number for part_number in part_numbers if is_adjacent(symbol, part_number)
    }
    return symbol, adjacent_part_numbers


def is_gear(symbol_and_parts: tuple[Symbol, set[PartNumber]]) -> bool:
    symbol, part_numbers = symbol_and_parts
    return len(part_numbers) == 2


def get_gear_ratio(symbol_and_parts: tuple[Symbol, set[PartNumber]]) -> int:
    symbol, (part_1, part_2) = symbol_and_parts
    return part_1.value * part_2.value


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    schematics = parse(lines)
    symbols = sorted(schematics.symbols, key=lambda x: (x.row, x.column))
    part_numbers = sorted(
        schematics.part_numbers, key=lambda x: (x.row, x.start_column)
    )
    star_symbols = filter(lambda s: s.value == "*", symbols)
    symbols_with_adjacent_part_numbers = map(
        partial(get_adjacent_part_numbers, part_numbers), star_symbols
    )
    gears = filter(is_gear, symbols_with_adjacent_part_numbers)
    gear_ratios = map(get_gear_ratio, gears)
    return str(sum(gear_ratios))


if __name__ == "__main__":
    setup_logging()
    main()
