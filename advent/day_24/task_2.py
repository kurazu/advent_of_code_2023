import itertools as it
import logging
from pathlib import Path
from typing import Any, Iterable

import sympy as sp
from contexttimer import Timer

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Particle, parse_particle

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    particles = list(map(parse_particle, lines))

    stone_slope_x = sp.Symbol("st_slope_x")
    stone_slope_y = sp.Symbol("st_slope_y")
    stone_slope_z = sp.Symbol("st_slope_z")
    stone_intercept_x = sp.Symbol("st_intercept_x")
    stone_intercept_y = sp.Symbol("st_intercept_y")
    stone_intercept_z = sp.Symbol("st_intercept_z")

    t_variables: list[sp.Symbol] = []
    equations: list[sp.Eq] = []

    for i, particle in enumerate(it.islice(particles, 0, 3)):
        t = sp.Symbol(f"t_{i}")
        t_variables.append(t)
        # stone clashes with particle on X asis
        equations.append(
            sp.Eq(particle.vx * t + particle.x, stone_slope_x * t + stone_intercept_x)
        )
        # stone clashes with particle on Y asis
        equations.append(
            sp.Eq(particle.vy * t + particle.y, stone_slope_y * t + stone_intercept_y)
        )
        # stone clashes with particle on Z asis
        equations.append(
            sp.Eq(particle.vz * t + particle.z, stone_slope_z * t + stone_intercept_z)
        )

    logger.debug(
        "Solving %d equations with %d time variables",
        len(equations),
        len(t_variables),
    )
    with Timer() as timer:
        solutions = sp.solve(
            equations,
            [
                stone_slope_x,
                stone_slope_y,
                stone_slope_z,
                stone_intercept_x,
                stone_intercept_y,
                stone_intercept_z,
                *t_variables,
            ],
            dict=True,
            diophantine=True,
        )
    logger.debug("Solving took %.1fs", timer.elapsed)
    logger.debug("Solutions:\n%s", solutions)
    (solution,) = solutions
    x = solution[stone_intercept_x]
    y = solution[stone_intercept_y]
    z = solution[stone_intercept_z]
    logger.info("Stone position: x=%s, y=%s, z=%s", x, y, z)
    return str(x + y + z)


if __name__ == "__main__":
    setup_logging()
    main()
