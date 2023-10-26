"""
Parse Lahjoita Puhetta metadata to support queries
"""

import json
import pathlib
import argparse


class Schedule:
    def __init__(self, path, lang):
        path = pathlib.Path(path)
        j = json.load(open(path))
        self._id = j["scheduleId"]
        assert self._id == path.stem
        prompts = filter(lambda x: x["kind"] == "prompt", j["items"])
        recordings = filter(lambda x: x["isRecording"] is True, j["items"])
        self.prompts = {prompt["itemId"]: prompt["title"][lang] for prompt in prompts}
        self.recordings = {
            recording["itemId"]: {
                "title": recording["title"][lang],
                "body": recording["body1"][lang] + "\n" + recording["body2"][lang],
            }
            for recording in recordings
        }


class Theme:
    def __init__(self, path, args):
        path = pathlib.Path(path)
        j = json.load(open(path))
        assert len(j["title"].keys()) == 1
        self.lang = list(j["title"].keys())[0]
        self._id = path.stem
        self.scheduleIds = list(j["scheduleIds"])
        self.schedules = [
            Schedule(args.schedule_dir / f"{Id}.json", self.lang)
            for Id in self.scheduleIds
        ]


def parse_themes(args):
    return [Theme(path, args) for path in args.theme_dir.iterdir()]


def get_base_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--theme-dir",
        default="./theme/",
        type=pathlib.Path,
        help="Directory for LP themes, eg. theme/",
    )
    argparser.add_argument(
        "--schedule-dir",
        default="./configuration/",
        type=pathlib.Path,
        help="Directory for schedules, eg. configuration/",
    )
    return argparser


if __name__ == "__main__":
    argparser = get_base_argparser()
    args = argparser.parse_args()
    themes = parse_themes(args)
    for theme in themes:
        for schedule in theme.schedules:
            print(schedule.prompts)
