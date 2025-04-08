import requests
import json
import argparse
import os
import time

base_url = "https://kielipankki.rahtiapp.fi/audio/asr/fi"
submit_url = base_url + "/submit_file"
query_url = base_url + "/query_job"


def float_to_srt_timestamp(t):
    hours = int(t / (60 * 60))
    t -= hours * 60 * 60
    minutes = int(t / 60)
    t -= minutes * 60
    seconds = int(t)
    t -= seconds
    milliseconds = int(round(t, 3) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def print_subtitles(subtitle_frames):
    for i, sub in enumerate(subtitle_frames):
        print(i + 1)
        print(float_to_srt_timestamp(sub[0]) + " --> " + float_to_srt_timestamp(sub[1]))
        print(sub[2])
        print()


def main():
    parser = argparse.ArgumentParser(description="Write a .srt file for audio segments")
    parser.add_argument(
        "--segment-file", default="segments.csv", help="CSV file with segment names"
    )
    args = parser.parse_args()
    subtitle_frames = []
    for line in open(args.segment_file):
        csv_parts = line.strip().split(";")
        path_to_audio_segment = csv_parts[0]
        audio_segment_filename = os.path.basename(path_to_audio_segment)
        timestamps = csv_parts[1]
        time_start, time_stop = (float(t) for t in timestamps.split(","))
        response = requests.post(
            submit_url,
            files={"file": (audio_segment_filename, open(path_to_audio_segment, "rb"))},
        )
        response_dict = json.loads(response.text)
        time_to_sleep = 1
        while True:
            time.sleep(time_to_sleep)
            query_response = requests.post(query_url, data=response_dict["jobid"])
            query_response_dict = json.loads(query_response.text)
            is_pending = (
                "status" in query_response_dict
                and query_response_dict["status"] == "pending"
            )
            incomplete = (
                "done" in query_response_dict and query_response_dict["done"] == False
            )
            if is_pending or incomplete:
                time_to_sleep += 1
            else:
                break
        cumulative_duration = time_start
        for segment in query_response_dict["segments"]:
            # these are segments from the ASR endpoint, not our segments
            offset = float(segment["duration"])
            transcript = segment["responses"][0]["transcript"]
            if len(transcript) > 0:
                subtitle_frames.append(
                    [
                        cumulative_duration,
                        time_start + offset,
                        transcript,
                    ]
                )
            cumulative_duration = time_start + offset

    print_subtitles(subtitle_frames)


if __name__ == "__main__":
    main()
