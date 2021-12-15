"""just some general things here"""
import re
from pathlib import Path
from typing import Set

SURVERY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe4zwAsOisipPy9Jr1OW19zmaspXh-w0aLaUzbSQt3t2o0Utg" \
              "/viewform?usp=pp_url&entry.851864411={chip_id:X}"
# https://stevesammons.me/dynamically-pre-fill-google-forms-with-url-parameters/

DATETIME_FMT = "%Y/%m/%d %H:%M:%S"

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
CHIP_ID_REGEX = re.compile(r"^[0-9]{4}$")

STORAGE_PATH = (Path(__file__) / "../../../storage/").resolve()
CHIPS_PATH = STORAGE_PATH / "chips.txt"
DATABASE_PATH = STORAGE_PATH / "db.sqlite3"


valid_chips: Set[int] = set()
