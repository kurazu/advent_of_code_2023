import logging
from dataclasses import dataclass
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@dataclass
class Dice:
    red: int
    green: int
    blue: int


@dataclass
class Game:
    id: int
    rolls: list[Dice]


def parse_roll(line: str) -> Dice:
    # Sample: "1 green, 3 red, 6 blue"
    result = Dice(red=0, green=0, blue=0)
    segments = map(str.strip, line.split(","))
    for segment in segments:
        amount, color = segment.split(" ")
        if color == "red":
            result.red = int(amount)
        elif color == "green":
            result.green = int(amount)
        elif color == "blue":
            result.blue = int(amount)
        else:
            raise ValueError(f"Unknown color {color!r}")
    return result


def parse_game(line: str) -> Game:
    # Sample: "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red"
    assert line.startswith("Game ")
    id, rest = line[5:].split(":", 1)
    game_id = int(id)
    rolls = [parse_roll(roll.strip()) for roll in rest.split(";")]
    return Game(id=game_id, rolls=rolls)


def has_at_least(game: Game, constraint: Dice) -> bool:
    return all(
        roll.red <= constraint.red
        and roll.green <= constraint.green
        and roll.blue <= constraint.blue
        for roll in game.rolls
    )


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    games = map(parse_game, lines)
    constraint = Dice(red=12, green=13, blue=14)
    valid_games = filter(lambda game: has_at_least(game, constraint), games)
    ids = map(lambda game: game.id, valid_games)
    return str(sum(ids))


if __name__ == "__main__":
    setup_logging()
    main()
