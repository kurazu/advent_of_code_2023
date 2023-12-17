import logging
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, {c: int(c) for c in "123456789"})
    logger.debug("Board:\n%s", board)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
