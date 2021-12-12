#!/usr/bin/python
import logging
import sys

from telegram.ext import Updater

from lib import (
    utils,
    # mailer,
    resources as rss,
    bot_builder,
    database,
)

if __name__ == "__main__":
    # init
    args = utils.Args.parse(sys.argv)
    rss.valid_chips.update(utils.parse_chips(rss.CHIPS_PATH))
    database.db_init(db_path=rss.DATABASE_PATH)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.logging_level)
    # mailer.init_data_mailer(args.email, [args.email, ], args.email_pass)
    updater = bot_builder.build_bot(Updater(args.token,))

    # work
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

    # shutdown
    db_thread, db_path = database.db_terminate()
    db_thread.join()
    # mailer.send_data_files([db_path, ], consume_attachments=False)A
