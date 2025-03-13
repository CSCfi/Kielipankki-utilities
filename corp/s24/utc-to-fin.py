#! /usr/bin/env pytho3

"""
utc-to-fin.py

Convert all UTC timestamps of the form "YYYY-MM-DD hh:mm:ss"
recognized in the input text to Finnish local time. Read from standard
input and write to standard output.
"""


import sys
import re
from datetime import datetime, timezone

from zoneinfo import ZoneInfo

zfin = ZoneInfo("Europe/Helsinki")


def convert_fin(mo):
    dt = datetime.fromisoformat(mo.group(0))
    return dt.replace(tzinfo=timezone.utc).astimezone(zfin).strftime('%Y-%m-%d %H:%M:%S')


def main():
    datetime_re = re.compile('\d{4}(?:-\d\d){2} \d\d(?::\d\d){2}')
    for line in sys.stdin:
        sys.stdout.write(datetime_re.sub(convert_fin, line))


if __name__ == '__main__':
    main()
