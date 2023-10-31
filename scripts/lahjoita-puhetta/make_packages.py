"""
Output a bash file with aws cli commands to fetch a collection of audio files
"""

import sys
import pathlib
import json
import random
import re
import subprocess

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


def download_audio(path, args):
    parts = path.parts
    while not looks_like_uuid(parts[0]):
        parts = parts[1:]
    target_path = "/".join(parts[:-1])  # just the directory
    result = subprocess.run(
        [
            "aws",
            "s3",
            "sync",
            "--exclude",
            "*",
            "--include",
            f"{path.stem}.*",
            "--exclude",
            "*.json",
            f"s3://vake-puhe-content-prod/uploads/audio_and_metadata/{target_path}",
            f"{args.download_dir}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    downloaded_files = re.findall(
        rf"download: .+({args.download_dir}[^\n]+)\n", result.stdout.decode()
    )
    assert len(downloaded_files) == 1
    return pathlib.Path(downloaded_files[0])


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


def is_silent(path, duration):
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            path,
            "-af",
            "silencedetect=noise=-50dB:d=1",  # detect silences below -50dB of over 1 sec duration
            "-f",
            "null",
            "-",  # don't write an output file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    total_silence = sum(
        [
            float(duration)
            for duration in re.findall(
                r"silence_duration: (.+)\n", result.stderr.decode()
            )
        ]
    )
    return total_silence / duration > 0.9


if __name__ == "__main__":
    argparser = get_base_argparser()
    argparser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    argparser.description = """Make packages of Lahjoita Puhetta audio files for sending to transcription services.

    This program assumes the presence of metadata describing the service ("theme" and "schedule"), and of course the metadata of the recordings themselves ("metadata"). It also assumes an aws client configured for s3 access to the Lahjoita Puhetta production site (read-only access is enough), and ffmpeg for ignoring silent files.

    The program also writes a log of correspondences between UUIDs and file numbers. Keep this file around, it is your record of what is what. It is also used (by appending to if it already exists) to avoid repeating the same files if you are making multiple packages. The file can be controlled with command line options.

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
        "--package_log_file",
        type=pathlib.Path,
        help="Path to write or append a log of UUID-file number correspondences",
        default=pathlib.Path("./uuid-files.log"),
    )
    argparser.add_argument("--info", action="store_true", help="Print information only")
    argparser.add_argument(
        "--download-dir",
        type=pathlib.Path,
        default=pathlib.Path("./audio"),
        help="Path where aws will be told to download files.",
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

    ignore_list = []
    next_file_number = 1
    if (
        args.package_log_file != argparser.get_default("package_log_file")
        or args.package_log_file.exists()
    ):
        # try to read the log if the user set one or if the default one exists
        for line in open(args.package_log_file):
            parts = line.strip().split()
            ignore_list.append(parts[0])
            try:
                next_file_number = max(next_file_number, int(parts[1]))
            except ValueError:
                continue  # this was a rejected file we want to ignore
    ignore_set = set(ignore_list)

    def recording_selection_filter(r):
        return (
            r["itemId"] in wanted_itemIds
            and args.min_duration < r["recordingDuration"] < args.max_duration
            and r["recordingId"] not in ignore_set
        )

    recordings = load_recordings_metadata(args, filter_fun=recording_selection_filter)
    random.seed(args.random_seed)
    random.shuffle(recordings)

    print("\nDownloading audio...", file=sys.stderr)
    recordings_added = []
    tally = 0
    orig_next_file_number = next_file_number
    for recording in recordings:
        if tally + recording["duration"] > args.package_size:
            break
        filepath = download_audio(recording["path"], args)
        if is_silent(filepath, recording["duration"]):
            filepath.unlink()
            recordings_added.append((recording["recordingId"], "SKIPPED_SILENCE"))
            print(
                f'REJECTED {recording["recordingId"]} due to silence', file=sys.stderr
            )
            continue
        tally += recording["duration"]
        recordings_added.append((recording["recordingId"], str(next_file_number)))
        new_filepath = filepath.with_stem(str(next_file_number))
        filepath.rename(new_filepath)
        print(f'ADDED {recording["recordingId"]} as {new_filepath}', file=sys.stderr)
        next_file_number += 1
        # print(make_aws_command(recording["path"], args))
    print(
        f"Saved {next_file_number - orig_next_file_number} files with a total duration of {time_format(tally)}",
        file=sys.stderr,
    )

    with open(args.package_log_file, mode="a", encoding="utf-8") as fobj:
        for uuid, target in recordings_added:
            print(uuid, target, file=fobj)
    print(f"\nWrote logs to {args.package_log_file}", file=sys.stderr)
