import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple
import logging
from . import resources as rss


@dataclass(frozen=True)
class Args:
    procname: str
    token: str
    email: str
    password: str
    logging_level: int = logging.DEBUG

    @classmethod
    def parse(cls, argv: List[str]) -> "Args":
        return cls(argv[1], argv[2], argv[3], argv[4], logging.__dict__[argv[5].upper()])


def parse_validate_chips(p: Path) -> Set[int]:
    if not p.exists():
        logging.getLogger(__name__).critical("""
storage/chips.txt is absent please create file and put there smth like this:
--------- storage/chips.txt -----------------
# comment lines start with #
# each chip id is a number on a separate line
5566
7788
---------------------------------------------
"""
        )

    with p.open("rt") as f:
        lines: List[Tuple[int, str]] = [(i+1, c) for (i, c) in enumerate(f.readlines()) if not c.startswith("#")]

    if len(lines) == 0:
        logging.getLogger(__name__).critical("storage/chips.txt empty")

    invalid = [(i, c) for i, c in lines if not rss.CHIP_ID_REGEX.match(c)]
    if len(invalid) > 0:
        l = logging.getLogger(__name__)
        l.critical(
            "Following invalid chips detected:\n" +
            "\n".join(f"{i}: {c}" for i, c in invalid)
        )
        sys.exit(1)

    return {int(c) for _, c in lines}
