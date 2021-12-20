#!/usr/bin/python
import logging
from pathlib import Path
from typing import Set

from setproctitle import setproctitle
from telegram.ext import Updater

from mylib import (
    resources as rss,
    bot_builder,
    database,
)

# ==================== configuration reading functions ==========================
default_cfg = {
    "process_title": "bot",
    "log_to_console": False,
    "logging_level": "debug",
    "api_token": "12345",
    "bot_password": None
}


def get_config(p: Path) -> dict:
    """attempts to write default config if file is not found"""
    from json import load, dump
    if not p.exists():
        with p.open("wt") as f:
            dump(default_cfg, f, indent=0)
            raise FileNotFoundError(f"file {p} did not exist, wrote default config into it")

    with p.open("rt") as f:
        cfg = load(f)
        cfg["logging_level"] = logging.__dict__[cfg["logging_level"].upper()]
        return cfg


default_chip_file = """
# comment lines start with `#`
# each chip id is a 4 digit decimal number on a separate line
0001  # because of additional text on the line this chip will be invalid
1234
"""


def get_chips(p: Path) -> Set[int]:
    """if file is not found attempts to write into that location a default file"""
    if not p.exists():
        with p.open("wt") as f:
            f.write(default_chip_file)
        raise FileNotFoundError(f"{p} did not exist, wrote default dummy list to that location")

    with p.open("rt") as f:
        lines = [(i+1, c) for (i, c) in enumerate(f.readlines()) if not c.startswith("#")]
    if len(lines) == 0:
        raise ValueError(f"chip file {p} is empty")
    invalid = [(i, c) for i, c in lines if not rss.CHIP_ID_REGEX.match(c)]
    if len(invalid) > 0:
        raise ValueError(
            "Following invalid chips detected:\n" +
            "\n".join(f"{i}: {c}" for i, c in invalid)
        )
    return {int(c) for _, c in lines}


# ================================ main ====================================================
if __name__ == "__main__":
    # read configs
    cfg = get_config(rss.STORAGE_PATH / "../private/bot_config.json")
    rss.valid_chips.update(get_chips(rss.CHIPS_PATH))
    del get_chips, get_config, default_chip_file, default_cfg

    # setup
    setproctitle(cfg["process_title"])  # send SIGTERM to this name to correctly terminate the bot
    logging.basicConfig(
        filename=None if cfg["log_to_console"] else rss.STORAGE_PATH / "bot.log",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=cfg["logging_level"],
    )
    database.db_init(db_path=rss.DATABASE_PATH)
    updater = bot_builder.build_bot(Updater(cfg["api_token"]), password=cfg["bot_password"])

    # work
    updater.start_polling()  # starts worker threads
    updater.idle()  # blocks main thread until SIGTERM, SIGABRT, SIGINT

    # shutdown
    db_thread, db_path = database.db_terminate()
    db_thread.join()
