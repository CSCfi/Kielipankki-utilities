"""
Output a bash file with aws cli commands to fetch a collection of audio files
"""

import sys
import pathlib
import json
import random
import re

from parse_lp_config import *


def num_format(num):
    return "{:,}".format(num)


def time_format(s):
    s = round(s)
    if s < 60:
        return f"{s} seconds"
    m = s // 60
    s -= 60 * m
    if m < 60:
        return f"{m} minutes, {s} seconds"
    h = m // 60
    m -= 60 * h
    return f"{h} hours, {m} minutes, {s} seconds"


def summarize_recordings(recordings):
    return f"{num_format(len(recordings))}, total {time_format(sum(map(lambda x: x['duration'], recordings)))}"


def walk(path):
    for p in path.iterdir():
        if p.is_dir():
            yield from walk(p)
            continue
        yield p


def load_recordings_metadata(args, filter_fun):
    retval = []
    count = 0
    print("Parsing metadata...", file=sys.stderr)
    for filepath in walk(args.metadata_dir):
        count += 1
        if count % 1000 == 0:
            print(f"{len(retval)}/{count}", end="\r", file=sys.stderr)
        j = json.load(open(filepath))
        if filter_fun(j):
            retval.append(
                {
                    "recordingId": j["recordingId"],
                    "duration": j["recordingDuration"],
                    "path": filepath,
                }
            )
    print(
        f"Parsed {count} metadata files, {len(retval)} recordings matched filter",
        file=sys.stderr,
    )
    return retval


def looks_like_uuid(s):
    return (
        re.match(r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", s)
        != None
    )


def make_aws_command(path, args):
    parts = path.parts
    name = path.stem
    while not looks_like_uuid(parts[0]):
        parts = parts[1:]
    target_path = "/".join(parts[:-1])  # just the directory
    return f'aws s3 sync --exclude "*" --include "{name}*" --exclude "*.json" s3://vake-puhe-content-prod/uploads/audio_and_metadata/{target_path} {args.download_dir}'


def info(wanted_itemIds, args):
    recordings = load_recordings_metadata(
        args, filter_fun=lambda r: r["itemId"] in wanted_itemIds
    )
    print(
        "Total duration " + time_format(sum(map(lambda x: x["duration"], recordings))),
        file=sys.stderr,
    )

    zero_sec = [r for r in recordings if r["duration"] == 0.0]
    upto_1_sec = [r for r in recordings if 0 < r["duration"] <= 1]
    upto_3_sec = [r for r in recordings if 1 < r["duration"] <= 3]
    upto_10_sec = [r for r in recordings if 3 < r["duration"] <= 10]
    upto_30_sec = [r for r in recordings if 10 < r["duration"] <= 30]
    upto_60_sec = [r for r in recordings if 30 < r["duration"] <= 60]
    upto_3_min = [r for r in recordings if 60 < r["duration"] <= 3 * 60]
    upto_10_min = [r for r in recordings if 3 * 60 < r["duration"] <= 10 * 60]
    over_10_min = [r for r in recordings if 10 * 60 < r["duration"]]

    print(f"Zero-length or otherwise invalid files: {summarize_recordings(zero_sec)}")
    print(f"Up to 3 seconds: {summarize_recordings(upto_3_sec)}")
    print(f"Up to 10 seconds: {summarize_recordings(upto_10_sec)}")
    print(f"Up to 30 seconds: {summarize_recordings(upto_30_sec)}")
    print(f"Up to 60 seconds: {summarize_recordings(upto_60_sec)}")
    print(f"Up to 3 minutes: {summarize_recordings(upto_3_min)}")
    print(f"Up to 10 minutes: {summarize_recordings(upto_10_min)}")
    print(f"Over 10 minutes: {summarize_recordings(over_10_min)}")


def round_robin_selection(upto_10_sec, upto_30_sec, upto_60_sec, upto_3_min, args):
    """
    Normally unused, this is just for making the "representative" trial set
    """
    tally = 0
    i = 0
    while tally <= 15 * 60:
        recording = (upto_10_sec, upto_30_sec, upto_60_sec, upto_3_min)[i % 4][i // 4]
        print(make_aws_command(recording["path"], args))
        tally += recording["duration"]
        i += 1


if __name__ == "__main__":
    argparser = get_base_argparser()
    argparser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    argparser.description = """Make packages of Lahjoita Puhetta audio files for sending to transcription services.

    This program assumes the presence of metadata describing the service ("theme" and "schedule"), and of course the metadata of the recordings themselves ("metadata"). It will output a series of aws commands, which you are then supposed to run as shell commands. You need to set up aws yourself.

    If you make more than one package, you'll want to avoid repeating the same files. To do this, figure out the UUIDs of the files you've already gotten and give a list of them to this program to ignore in the selection process.

    If you want to make a 60 minute package of Swedish audio files, ignoring files under 5 seconds, and you have the directories configuration/, theme/ and metadata/ present in the working directory, do:

    python make_packages.py --lang=sv --package-size=60 --min-duration=5 --ignore-from ignore.txt > commands_for_aws.txt # inspect this and then run with your shell command
    """
    argparser.add_argument("--lang", help="'sv' for Swedish, 'fi' for Finnish")
    argparser.add_argument(
        "--metadata-dir",
        type=pathlib.Path,
        default="./metadata/",
        help="Where to look for the metadata",
    )
    argparser.add_argument(
        "--random-seed", type=int, default=4, help="Random seed for replicability"
    )
    argparser.add_argument(
        "--min-duration", type=int, default=5, help="Per file, in seconds"
    )
    argparser.add_argument(
        "--max-duration",
        type=int,
        default=15 * 60,
        help="Per file, in seconds",
    )
    argparser.add_argument(
        "--package-size",
        default=60,
        type=lambda x: int(x) * 60,
        help="In minutes",
    )
    argparser.add_argument(
        "--ignore-ids-file",
        type=pathlib.Path,
        help="Path of file with list of recodingIds to ignore",
    )
    argparser.add_argument("--info", action="store_true", help="Print information only")
    argparser.add_argument(
        "--download-dir",
        type=pathlib.Path,
        default="./audio",
        help="Path where aws will be told to download files. If there are multiple packages being made, multiple directories will be created there.",
    )
    args = argparser.parse_args()

    themes = parse_themes(args)
    wanted_itemIds = set()
    for theme in themes:
        if args.lang in (None, theme.lang):
            for schedule in theme.schedules:
                wanted_itemIds.update(schedule.recordings.keys())

    if args.info:
        info(wanted_itemIds, args)
        exit(0)

    ignore_set = set()
    if args.ignore_ids_file:
        ignore_set.update([line.strip() for line in open(args.ignore_ids_file)])

    def recording_selection_filter(r):
        return (
            r["itemId"] in wanted_itemIds
            and args.min_duration < r["recordingDuration"] < args.max_duration
            and r["recordingId"] not in ignore_set
        )

    recordings = load_recordings_metadata(args, filter_fun=recording_selection_filter)
    random.seed(args.random_seed)
    random.shuffle(recordings)

    tally = 0
    for recording in recordings:
        if tally + recording["duration"] > args.package_size:
            break
        tally += recording["duration"]
        print(make_aws_command(recording["path"], args))
