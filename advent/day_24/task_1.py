import itertools as it
import logging
import math
from pathlib import Path
from typing import Any, Iterable, NamedTuple

import more_itertools as mit
from sympy import solve
from sympy.abc import a, b, c, d, e, f, g, h, x, y
from tqdm import tqdm

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Particle(NamedTuple):
    x: int
    y: int
    z: int
    vx: int
    vy: int
    vz: int


def parse_particle(line: str) -> Particle:
    position_part, velocity_part = line.split(" @ ")
    position = map(int, position_part.split(","))
    velocity = map(int, velocity_part.split(","))
    return Particle(*position, *velocity)


a_time = x
b_time = y
a_x_slope = a
a_x_intercept = b
a_y_slope = c
a_y_intercept = d
b_x_slope = e
b_x_intercept = f
b_y_slope = g
b_y_intercept = h

a_x = a_x_slope * a_time + a_x_intercept
a_y = a_y_slope * a_time + a_y_intercept
b_x = b_x_slope * b_time + b_x_intercept
b_y = b_y_slope * b_time + b_y_intercept


class Intersection(NamedTuple):
    x: float
    y: float
    t_a: float
    t_b: float


def find_intersection(
    *, a_time_solution: Any, b_time_solution: Any, a: Particle, b: Particle
) -> Intersection | None:
    # logger.debug("Finding intersection of %s and %s", a, b)

    vars: dict[Any, float] = {
        a_x_slope: a.vx,
        a_x_intercept: a.x,
        a_y_slope: a.vy,
        a_y_intercept: a.y,
        b_x_slope: b.vx,
        b_x_intercept: b.x,
        b_y_slope: b.vy,
        b_y_intercept: b.y,
    }

    a_t_evaluated = a_time_solution.subs(vars).evalf()
    b_t_evaluated = b_time_solution.subs(vars).evalf()
    if not a_t_evaluated.is_finite or not b_t_evaluated.is_finite:
        logger.warning("No intersection between %s and %s", a, b)
        return None
    a_t = float(a_t_evaluated)
    b_t = float(b_t_evaluated)

    vars = {
        **vars,
        a_time: a_t,
        b_time: b_t,
    }
    x = a_x.subs(vars).evalf()
    y = a_y.subs(vars).evalf()
    # logger.debug("x=%.3f y=%.3f", x, y)

    logger.debug(
        "Intersection of %s and %s is (x=%.3f, y=%.3f @ t_a=%.3f, t_b=%.3f)",
        a,
        b,
        x,
        y,
        a_t,
        b_t,
    )
    return Intersection(x=x, y=y, t_a=a_t, t_b=b_t)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    particles = list(map(parse_particle, lines))
    (solution,) = solve(
        [
            a_x - b_x,
            a_y - b_y,
        ],
        [
            a_time,
            b_time,
        ],
        dict=True,
    )
    a_time_solution = solution[a_time]
    b_time_solution = solution[b_time]

    n_combinations = math.comb(len(particles), 2)
    combinations = it.combinations(particles, 2)
    interactions: Iterable[Intersection | None] = it.starmap(
        lambda a, b: find_intersection(
            a_time_solution=a_time_solution, b_time_solution=b_time_solution, a=a, b=b
        ),
        tqdm(combinations, total=n_combinations),
    )

    intersections: Iterable[Intersection] = filter(None, interactions)

    min_x = min_y = 7
    max_x = max_y = 27

    min_x = min_y = 200000000000000
    max_x = max_y = 400000000000000

    intersections_in_present = filter(
        lambda intersection: (intersection.t_a >= 0) and (intersection.t_b >= 0),
        intersections,
    )
    intersections_in_area = filter(
        lambda intersection: (min_x <= intersection.x <= max_x)
        and (min_y <= intersection.y <= max_y),
        intersections_in_present,
    )

    number_of_intersections = mit.ilen(intersections_in_area)
    return str(number_of_intersections)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
