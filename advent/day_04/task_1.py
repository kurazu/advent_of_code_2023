import logging
from dataclasses import dataclass
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@dataclass
class Card:
    id: int
    winning: set[int]
    have: set[int]


def parse_card(line: str) -> Card:
    id_part, rest = line.split(":", 1)
    _, id_part = id_part.split()
    id = int(id_part)
    winning_part, have_part = rest.split(" | ")
    winning_part = winning_part.strip()
    have_part = have_part.strip()
    winning = set(map(int, winning_part.split()))
    have = set(map(int, have_part.split()))
    return Card(
        id=id,
        winning=winning,
        have=have,
    )


def get_number_of_matches(card: Card) -> int:
    return len(card.winning.intersection(card.have))


def get_points(number_of_matches: int) -> int:
    return (2 ** (number_of_matches - 1)) if number_of_matches > 0 else 0


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    cards = map(parse_card, lines)
    number_of_matches = map(get_number_of_matches, cards)
    points = map(get_points, number_of_matches)
    return str(sum(points))


if __name__ == "__main__":
    setup_logging()
    main()
