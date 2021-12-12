"""
module for email sending utility functions. `send_email(...)` is the main interest.
adopted from https://www.codespeedy.com/send-email-with-file-attachment-in-python-with-smtp/
"""


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Iterable


def make_file_attachment(path: Path, consume_attachments=True) -> MIMEBase:
    attachment = MIMEBase('application', 'octet-stream')
    with open(path, "rb") as f:
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', "attachment; filename= " + path.name)
    if consume_attachments:
        path.unlink()
    return attachment


def compose_message(from_: str, to_: List[str], subject: str, text: str, attachments: Iterable[MIMEBase]) -> str:
    message = MIMEMultipart()
    message["From"] = from_
    message["to"] = "; ".join(to_)
    message["Subject"] = subject
    message.attach(MIMEText(text, _charset="utf-8"))
    for a in attachments:
        message.attach(a)
    return message.as_string()


def send_message(from_: str, to_: List[str], server: str, password: str, message: str):
    email_session = smtplib.SMTP(server, 587)
    email_session.starttls()
    email_session.login(from_, password)
    email_session.sendmail(from_, to_, message)
    email_session.quit()


def send_email(from_: str, to_: List[str], server: str, password: str, subject: str, text: str, attach: Iterable[Path],
               consume_attachments=True):
    """may take several (1-10) seconds"""
    msg = compose_message(from_, to_, subject, text, [make_file_attachment(a, consume_attachments) for a in attach])
    send_message(from_, to_, server, password, msg)
