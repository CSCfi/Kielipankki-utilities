"""Do perfomance checking on a Korp instance"""

import urllib
from urllib import request
import json
import argparse
import time
import random
import numpy

korp_url = "https://www.kielipankki.fi/korp/api8"

simple_query_cqp = 'word="h%C3%A4n"'


def time_format(s):
    if s < 60:
        return f"{s:.2f} seconds"
    m = int(s / 60)
    s -= 60 * m
    if m < 60:
        return f"{m} minutes, {s:.2f} seconds"
    h = int(m / 60)
    m -= 60 * h
    return f"{h} hours, {m} minutes, {s:.2f} seconds"


def query_korp_with_args(base_url, argdict):
    if "cache" not in argdict:
        argdict["cache"] = "false"
    assert "command" in argdict
    command = argdict["command"]
    del argdict["command"]
    url_args = "&".join((f"{k}={v}" for k, v in argdict.items()))
    response = request.urlopen(f"{base_url}/{command}?{url_args}")
    return json.loads(response.read())


def get_info(base_url):
    return query_korp_with_args(base_url, {"command": "info"})


def corpora_from_info(info):
    return {
        "corpora": info["corpora"],
        "protected_corpora": info["protected_corpora"],
        "public_corpora": [
            c for c in info["corpora"] if c not in info["protected_corpora"]
        ],
    }


def corpus_info_perf(args, corpora=None):
    times = []
    if corpora == None:
        for _ in range(args.n_times):
            starttime = time.time()
            get_info(args.base_url)
            times.append(time.time() - starttime)
    else:
        for _ in range(args.n_times):
            starttime = time.time()
            query_korp_with_args(
                args.base_url, {"command": "corpus_info", "corpus": ",".join(corpora)}
            )
            times.append(time.time() - starttime)
    return times


def simple_query_perf(args, corpora):
    times = []
    for _ in range(args.n_times):
        starttime = time.time()
        make_simple_query(args.base_url, corpora)
        times.append(time.time() - starttime)
    return times


def make_simple_query(base_url, corpora):
    return query_korp_with_args(
        args.base_url,
        {
            "command": "query",
            "cqp": simple_query_cqp,
            "corpus": ",".join(corpora),
            "start": 0,
            "end": 0,
            "cut": 0,
        },
    )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--base-url",
        default=korp_url,
        help=f"URL of Korp server, default is {korp_url}",
    )
    argparser.add_argument(
        "--n-times",
        default=5,
        type=int,
        help=f"How many times to run each operation (default is 5)",
    )
    argparser.add_argument(
        "--load",
        default=1,
        type=int,
        help=f"What percentage of corpora to query (default is 1%)",
    )
    argparser.add_argument("--seed", default=4, help=f"Set random seed to this value")
    args = argparser.parse_args()

    random.seed(args.seed)

    print()
    print(
        f"Running corpus_info without arguments {args.n_times} times on {args.base_url}... "
    )
    times = corpus_info_perf(args)
    print(
        f"Completed in {time_format(sum(times))}, average {time_format(sum(times)/args.n_times)}, stddev {numpy.std(times):.2f}"
    )
    corpora = corpora_from_info(get_info(args.base_url))
    corpora_to_test = [
        corpus
        for corpus in corpora["public_corpora"]
        if random.random() < 0.01 * args.load
    ]
    print(
        f"Running corpus_info on specific random corpora {args.n_times} times on {args.base_url}... "
    )
    times = corpus_info_perf(args, corpora_to_test)
    print(
        f"Completed in {time_format(sum(times))}, average {time_format(sum(times)/args.n_times)}, stddev {numpy.std(times):.2f}"
    )
    print()

    print(
        f"Running {args.n_times} simple queries on specific random public corpora on {args.base_url}... "
    )
    times = simple_query_perf(args, corpora_to_test)
    print(
        f"Completed in {time_format(sum(times))}, average {time_format(sum(times)/args.n_times)}, stddev {numpy.std(times):.2f}"
    )
    print()
