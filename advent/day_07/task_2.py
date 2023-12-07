import itertools as it
import logging
from collections import Counter
from pathlib import Path
from typing import Iterable, NamedTuple, TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


SYMBOL_TO_CARD_VALUE: dict[str, int] = {c: v for v, c in enumerate("AKQT98765432J", 1)}
CARD_VALUE_TO_SYMBOL: dict[int, str] = {v: k for k, v in SYMBOL_TO_CARD_VALUE.items()}

Cards: TypeAlias = list[int]


class Hand(NamedTuple):
    cards: Cards
    bid: int

    def __repr__(self) -> str:
        return "".join(map(CARD_VALUE_TO_SYMBOL.__getitem__, self.cards))


HandType: TypeAlias = dict[int, int]

HAND_TYPE_VALUES: list[tuple[HandType, int]] = [
    (card_type, value)
    for value, card_type in enumerate(
        [
            {5: 1},
            {4: 1, 1: 1},
            {3: 1, 2: 1},
            {3: 1, 1: 2},
            {2: 2, 1: 1},
            {2: 1, 1: 3},
            {1: 5},
        ],
        1,
    )
]


def get_hand_type(cards: Cards) -> HandType:
    joker_value = SYMBOL_TO_CARD_VALUE["J"]
    number_of_jokers = cards.count(joker_value)
    cards_without_jokers = (c for c in cards if c != joker_value)
    # hand = [1, 1, 2, 3, 2]
    card_counter = Counter(cards_without_jokers)
    if not card_counter:
        card_counter[SYMBOL_TO_CARD_VALUE["A"]] = 0
    ((most_common_card, most_common_card_count),) = card_counter.most_common(1)
    card_counter[most_common_card] += number_of_jokers
    # card_counter = {1: 2, 2: 2, 3: 1}
    counts_counter = Counter(card_counter.values())
    # counts_counter = {2: 2, 1: 1}
    return counts_counter


def get_hand_type_value(hand_type: HandType) -> int:
    for possible_type, value in HAND_TYPE_VALUES:
        if possible_type == hand_type:
            return value
    raise AssertionError(f"Unrecognized hand type: {hand_type!r}")


def parse_hands(lines: Iterable[str]) -> Iterable[Hand]:
    for line in lines:
        cards_raw, bid_raw = line.split()
        cards = [SYMBOL_TO_CARD_VALUE[c] for c in cards_raw]
        bid = int(bid_raw)
        yield Hand(cards=cards, bid=bid)


def get_hand_score(hand: Hand) -> tuple[int, ...]:
    return get_hand_type_value(get_hand_type(hand.cards)), *hand.cards


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    hands = parse_hands(lines)
    sorted_hands = sorted(hands, key=get_hand_score, reverse=True)
    hands_with_ranks = enumerate(sorted_hands, 1)
    winnings = it.starmap(lambda rank, hand: rank * hand.bid, hands_with_ranks)
    return str(sum(winnings))


if __name__ == "__main__":
    setup_logging()
    main()
