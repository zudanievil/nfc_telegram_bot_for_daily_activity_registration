"""this script should convert ../storage/db.sqlite3 to plain-text tables"""
import sys
from datetime import datetime


def _check(cond: bool, err_msg: str):
    if not cond:
        print(err_msg, file=sys.stderr)
        sys.exit(1)


_check(__name__ == "__main__", err_msg="decode_db.py is a script, it cannot be imported")

from pathlib import Path
import sqlite3 as sql
from typing import List
from dataclasses import dataclass
from collections import namedtuple
from mylib import (database, resources as rss)


def read_Actions(conn: sql.Connection) -> List[database.ActionData]:
    return list(
        database.ActionData(user, datetime.fromtimestamp(time), database.actions(action))
        for (_, user, time, action) in conn.execute(database._READ_ACTIONS_BY_ID).fetchall()
    )  # todo: move this to database.ActionData.from_db


# todo: move to database ==============================
_READ_ALL_USERS = "SELECT user, chip, email FROM Users"


@dataclass(frozen=True)
class UserData:
    user: int
    chip: int
    email: str

    @classmethod
    def from_db(cls, db_conn: sql.Connection) -> List["UserData"]:
        return list(cls(*x) for x in db_conn.execute(_READ_ALL_USERS).fetchall())


# ================================================================


def read_Users(conn: sql.Connection) -> List[UserData]:
    return UserData.from_db(conn)


@dataclass(frozen=True)
class TableRow:
    time: datetime
    user: int
    email: str
    chip: int
    action: database.actions

    @classmethod
    def join(cls, a: database.ActionData, u: UserData) -> "TableRow":
        return cls(a.time, a.user, u.email, u.chip, a.action)

    def to_str(self, sep: str = "\t", date_fmt=rss.DATETIME_FMT) -> str:
        return sep.join((
            self.time.strftime(date_fmt),
            self.action.name,
            "" if self.email is None else self.email,
            str(self.chip),
            str(self.user),
        ))

    @staticmethod
    def header(sep="\t") -> str:
        return sep.join(("time", "action", "email", "chip_id", "tg_id"))


if __name__ == "__main__":
    out_path = rss.STORAGE_PATH / "db_copy.txt"
    db_path = rss.STORAGE_PATH / "db_copy.sqlite3"
    _check(db_path.exists(), err_msg=f"{db_path} does not exist.")
    conn = sql.connect(db_path)
    user_dict = {user.user: user for user in read_Users(conn)}
    rows = [TableRow.join(action, user_dict[action.user]) for action in read_Actions(conn)]
    conn.close()
    del user_dict

    with out_path.open("wt") as f:
        f.write(TableRow.header() + "\n")
        for row in rows:
            f.write(row.to_str() + "\n")
    print("Success")
