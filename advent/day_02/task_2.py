import logging
import string
from dataclasses import dataclass
from itertools import starmap
from pathlib import Path
from typing import Tuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Dice, Game, parse_game

logger = logging.getLogger(__name__)


def get_min_set(game: Game) -> Dice:
    return Dice(
        red=max(roll.red for roll in game.rolls),
        green=max(roll.green for roll in game.rolls),
        blue=max(roll.blue for roll in game.rolls),
    )


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    games = map(parse_game, lines)
    min_sets = map(get_min_set, games)
    powers = map(lambda x: x.red * x.green * x.blue, min_sets)
    return str(sum(powers))


if __name__ == "__main__":
    setup_logging()
    main()
