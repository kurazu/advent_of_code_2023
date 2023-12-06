import pytest

from .task_2 import Range, intersect

INTERSECT_TEST_CASES: list[tuple[Range, Range, list[tuple[Range, bool]]]] = [
    # no overlap, base before other
    (
        Range(start=0, end=10),
        Range(start=20, end=30),
        [
            (Range(start=0, end=10), False),
        ],
    ),
    # no overlap, base after other
    (
        Range(start=20, end=30),
        Range(start=0, end=10),
        [
            (Range(start=20, end=30), False),
        ],
    ),
    # exact overlap
    (
        Range(start=0, end=10),
        Range(start=0, end=10),
        [(Range(start=0, end=10), True)],
    ),
    # partial overlap, base before other
    (
        Range(start=0, end=10),
        Range(start=5, end=15),
        [
            (Range(start=0, end=5), False),
            (Range(start=5, end=10), True),
        ],
    ),
    # partial overlap, base after other
    (
        Range(start=5, end=15),
        Range(start=0, end=10),
        [
            (Range(start=5, end=10), True),
            (Range(start=10, end=15), False),
        ],
    ),
    # partial overlap, base contains other
    (
        Range(start=0, end=20),
        Range(start=5, end=15),
        [
            (Range(start=0, end=5), False),
            (Range(start=5, end=15), True),
            (Range(start=15, end=20), False),
        ],
    ),
    # partial overlap, other contains base
    (
        Range(start=5, end=15),
        Range(start=0, end=20),
        [
            (Range(start=5, end=15), True),
        ],
    ),
    # partial overlap, other contains base, base starts before other
    (
        Range(start=5, end=10),
        Range(start=0, end=10),
        [
            (Range(start=5, end=10), True),
        ],
    ),
    #
    (
        Range(start=5, end=10),
        Range(start=5, end=15),
        [
            (Range(start=5, end=10), True),
        ],
    ),
    #
    (
        Range(start=0, end=10),
        Range(start=5, end=10),
        [
            (Range(start=0, end=5), False),
            (Range(start=5, end=10), True),
        ],
    ),
    #
    (
        Range(start=0, end=10),
        Range(start=0, end=5),
        [
            (Range(start=0, end=5), True),
            (Range(start=5, end=10), False),
        ],
    ),
]


@pytest.mark.parametrize("base,other,expected", INTERSECT_TEST_CASES)
def test_intersect(
    base: Range, other: Range, expected: list[tuple[Range, bool]]
) -> None:
    actual = list(intersect(base=base, other=other))
    assert actual == expected
