#!/usr/bin/python
import logging
import sys

from setproctitle import setproctitle
from telegram.ext import Updater

from mylib import (
    utils,
    # mailer,
    resources as rss,
    bot_builder,
    database,
)

if __name__ == "__main__":
    # init
    args = utils.Args.parse(sys.argv)
    setproctitle(args.procname)  # send sigterm to this name to correctly terminate the bot
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.logging_level)
    rss.valid_chips.update(utils.parse_validate_chips(rss.CHIPS_PATH))
    database.db_init(db_path=rss.DATABASE_PATH)
    # mailer.init_data_mailer(args.email, [args.email, ], args.email_pass)
    updater = bot_builder.build_bot(Updater(args.token,), password="test")

    # work
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

    # shutdown
    db_thread, db_path = database.db_terminate()
    db_thread.join()
    # mailer.send_data_files([db_path, ], consume_attachments=False)
