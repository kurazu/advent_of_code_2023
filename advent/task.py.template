import logging
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
