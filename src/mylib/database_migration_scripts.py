"""scripts that help to coerce database to current version."""
# I've spent half an hour automating something that could be done in 2 minutes by hand.
# Totally worth it.

import sqlite3
from typing import Callable, List

_WRITE_VERSION = """UPDATE DBVersion SET version_number=?;"""
_READ_VERSION = """SELECT version_number FROM DBVersion;"""

UPDATER_TYPE = Callable[[sqlite3.Connection], None]


def update(conn: sqlite3.Connection, latest_version: int):
    """main script that updates database to LATEST_VERSION"""
    db_version = get_version(conn)
    namespace = globals()
    updaters: List[UPDATER_TYPE] = [namespace[f"_updater_{v}"] for v in range(db_version, latest_version)]
    for u in updaters:
        u(conn)
    set_version(conn, latest_version)
    conn.commit()


def set_version(conn: sqlite3.Connection, v: int):
    conn.execute(_WRITE_VERSION, (v, ))


def get_version(conn: sqlite3.Connection) -> int:
    try:
        return int(conn.execute(_READ_VERSION).fetchall()[0][0])
    except sqlite3.OperationalError:
        return 1


def _updater_1(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE DBVersion (version_number INTEGER NOT NULL);
    INSERT INTO DBVersion (version_number) values (2);
    ALTER TABLE Actions ADD description TEXT;""")

