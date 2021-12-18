#!/usr/bin/python
import logging
import sys

from setproctitle import setproctitle
from telegram.ext import Updater

from mylib import (
    misc,
    resources as rss,
    bot_builder,
    database,
)

if __name__ == "__main__":
    # init
    args = misc.Args.parse(sys.argv)
    setproctitle(args.procname)  # send sigterm to this name to correctly terminate the bot
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.logging_level)
    rss.valid_chips.update(misc.parse_validate_chips(rss.CHIPS_PATH))
    database.db_init(db_path=rss.DATABASE_PATH)
    updater = bot_builder.build_bot(Updater(args.token,), password=args.password)

    # work
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

    # shutdown
    db_thread, db_path = database.db_terminate()
    db_thread.join()
