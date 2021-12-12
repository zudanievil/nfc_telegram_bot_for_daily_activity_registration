"""singleton (module with global state) that manages emails"""

from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Optional, List, Iterable
from .email_utils import send_email
# from email_utils import send_email
import logging

_data_mailer: Optional[partial] = None
SENDING_RETRIES = 3


def init_data_mailer(from_: str, to_: List[str],  password: str, server="smtp.mail.ru", subject="telebot 51d66f7d data"):
    global _data_mailer
    _data_mailer = partial(send_email, from_=from_, to_=to_, server=server, password=password, subject=subject,)


def send_data_files(fs: Iterable[Path], consume_attachments=True):
    for _ in range(SENDING_RETRIES):
        try:
            _data_mailer(text=f"{datetime.now()}", attach=fs, consume_attachments=consume_attachments)
            logging.getLogger(__name__).info("email sent")
            return
        except Exception as e:
            logging.getLogger(__name__).info("email failed:", exc_info=e)


