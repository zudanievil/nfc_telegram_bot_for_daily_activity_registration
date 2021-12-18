import logging
import sqlite3 as sql
from typing import Union, Dict, List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Thread, Event
from queue import Queue
from time import sleep
from dataclasses import dataclass

# sql commands
_NEW_USER_TABLE = """
CREATE TABLE Users (
    user INTEGER NOT NULL PRIMARY KEY,
    chip INTEGER NOT NULL,
    email TEXT
);"""
_NEW_ACTION_TABLE = """
CREATE TABLE Actions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user INTEGER NOT NULL,
    date FLOAT NOT NULL,
    action INTEGER NOT NULL
);"""
_INSERT_ACTION = """INSERT INTO Actions (user, date, action) values (?, ?, ?)"""
_INSERT_EMAIL = """UPDATE Users
SET email=?
WHERE user=?"""
_NEW_CHIP = """INSERT INTO Users (user, chip) values (?, ?)"""
_INSERT_CHIP = """UPDATE Users
SET chip=?
WHERE user=?"""
_READ_USER_BY_ID = 'SELECT user, chip, email FROM Users WHERE user = ?'
_READ_ACTIONS_BY_ID = 'SELECT id, user, date, action FROM Actions'


class actions(Enum):
    food_carbo = 1
    food_other = 2
    sport = 3
    caffeine = 4
    nicotine = 5
    alcohol = 6


@dataclass(frozen=True)
class ActionData:
    user: int
    time: datetime
    action: actions

    def to_db(self, db_conn: sql.Connection):
        db_conn.execute(_INSERT_ACTION, (self.user, self.time.timestamp(), self.action.value))

    @classmethod
    def from_db(cls, db_conn: sql.Connection) -> List["ActionData"]:
        return list(
            cls(x[0], datetime.fromtimestamp(x[1]), actions(x[2]))
            for x in db_conn.execute(_READ_ACTIONS_BY_ID).fetchall()
        )


@dataclass(frozen=True)
class ChipData:
    user: int
    chip: int

    def to_db(self, db_conn: sql.Connection):
        try:
            db_conn.execute(_NEW_CHIP, (self.user, self.chip))
        except sql.IntegrityError:
            db_conn.execute(_INSERT_CHIP, (self.chip, self.user))
        db_conn.commit()

    def from_db(self, db_conn: sql.Connection) -> Optional["ChipData"]:
        try:
            _, chip, _ = db_conn.execute(_READ_USER_BY_ID, (self.user,)).fetchall()[0]
            return self.__class__(self.user, chip)
        except IndexError:
            return None


@dataclass(frozen=True)
class EmailData:
    user: int
    email: str

    def to_db(self, db_conn: sql.Connection):
        db_conn.execute(_INSERT_EMAIL, (self.email, self.user))


sqlite_writable_types = Union[ChipData, EmailData, ActionData]
# this could be an interface declaration, but python does not have interface keywords


# ================================ database singleton ==========================

__db_path: Path
__db_thread: Thread
__db_queue: Queue
__db_sigterm: Event


def db_init(db_path: Path):
    global __db_path
    global __db_thread
    global __db_queue
    global __db_sigterm
    __db_path = db_path
    __db_sigterm = Event()
    __db_queue = Queue()  # input type is (read_request_id, data): Tuple[Optional[int], sqlite_writable_types]
    __db_thread = Thread(target=_db_thread, name="db", args=(db_path, __db_queue, __db_sigterm))
    __db_thread.start()


def db_terminate() -> (Thread, Path):
    __db_sigterm.set()
    logging.getLogger(__name__).info("sigterm to db")
    return __db_thread, __db_path


def db_write(data: sqlite_writable_types):
    __db_queue.put((None, data))


def _db_thread(db_path: Path, task_queue: Queue, sigterm: Event,
               queue_poll_interval: float = 0.2):
    if db_path.exists():
        db_conn = sql.connect(db_path)
    else:
        db_conn = sql.connect(db_path)
        with db_conn:
            db_conn.execute(_NEW_USER_TABLE)
            db_conn.execute(_NEW_ACTION_TABLE)

    while True:
        if task_queue.empty():
            if sigterm.is_set():
                db_conn.commit()
                logging.getLogger(__name__).info("db terminated")
                break
            sleep(queue_poll_interval)
            continue
        read_request_id, data = task_queue.get()  # read_request_id: Optional[int]; data: sqlite_writable_types
        if read_request_id is None:
            data.to_db(db_conn)
            logging.getLogger(__name__).debug("db commit")
            db_conn.commit()
        else:
            __db_output[read_request_id] = data.from_db(db_conn)


__db_output: Dict[int, sqlite_writable_types] = dict()


@dataclass(frozen=True)
class _Read:
    request: int
    table: str
    key: int

    def from_db(self, conn: sql.Connection):
        pass


def db_read_user(user: int) -> Optional[ChipData]:
    __db_queue.put((user, ChipData(user, 0)))
    while user not in __db_output:
        sleep(0.05)
    logging.getLogger(__name__).debug("db read")
    return __db_output.pop(user)
