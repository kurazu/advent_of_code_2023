import logging
from collections import deque
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import get_number_of_matches, parse_card

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    cards = {card.id: card for card in map(parse_card, lines)}
    to_process = deque(cards)
    processed: int = 0
    while to_process:
        card = cards[to_process.popleft()]
        processed += 1
        number_of_matches = get_number_of_matches(card)
        to_process.extend(card.id + i for i in range(1, number_of_matches + 1))
    return str(processed)


if __name__ == "__main__":
    setup_logging()
    main()
