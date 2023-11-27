"""Run some checks on Korp corpora to see that they are returning expected results.
"""

import urllib
from urllib import request
import json
import argparse
import pathlib
import time

korp1_url = "https://korp.csc.fi/cgi-bin/korp/korp.cgi"
korp2_url = "https://kielipankki.fi/korp/api8"
simple_query_cqp = 'word="h%C3%A4n"'


OKGREEN = "\033[92m"
FAILRED = "\033[91m"
ENDCOLOR = "\033[0m"


def printterm(s, failed=True):
    if failed:
        print("[" + FAILRED + "FAIL" + ENDCOLOR + "] " + s)
    else:
        print("[" + OKGREEN + "OK" + ENDCOLOR + "] " + s)


def printlog(s, fobj, failed=True):
    if failed:
        print("[FAIL] " + s, file=fobj)
    else:
        print("[OK] " + s, file=fobj)


def report(s, log_fobj, failed=True):
    printterm(s, failed)
    printlog(s, log_fobj, failed)


def truncate(s):
    s = str(s)
    if len(s) <= 100:
        return s
    return f"{s:.97}..."


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


def query_korp_with_args(argdict, version):
    assert version in (1, 2)
    if version == 1:
        url_args = "&".join((f"{k}={v}" for k, v in argdict.items()))
        response = request.urlopen(f"{korp1_url}?{url_args}")
        return json.loads(response.read())

    elif version == 2:
        assert "command" in argdict
        command = argdict["command"]
        del argdict["command"]
        url_args = "&".join((f"{k}={v}" for k, v in argdict.items()))
        response = request.urlopen(f"{korp2_url}/{command}?{url_args}")
        return json.loads(response.read())


def get_info(version):
    return query_korp_with_args({"command": "info"}, version)


def corpora_from_info(info):
    return {
        "corpora": info["corpora"],
        "protected_corpora": info["protected_corpora"],
        "public_corpora": [
            c for c in info["corpora"] if c not in info["protected_corpora"]
        ],
    }


def make_simple_query(corpora, version):
    return query_korp_with_args(
        {
            "command": "query",
            "cqp": simple_query_cqp,
            "corpus": ",".join(corpora),
            "start": 0,
            "end": 0,
            "cut": 0,
        },
        version,
    )


def kwic_summary(kwic):
    charsum = 0
    for hit in kwic:
        charsum += sum(map(len, hit["tokens"]))
    return {"charsum": charsum}


def iterate_batch(batch, result_dict, version):
    """If a batch has a problem, we go over it in more detail"""
    for corpus in batch:
        result_dict["corpora_processed"] += 1
        try:
            single_result = make_simple_query([corpus], version)
        except urllib.error.HTTPError:
            print(f"      {corpus} failed with an HTTPError")
        if "ERROR" in single_result:
            print(f'      {corpus}: {single_result["ERROR"]}')
        else:
            try:
                result_dict["hits"] += int(single_result["hits"])
                result_dict["corpus_hits"].update(single_result["corpus_hits"])
                result_dict["kwic"] += single_result["kwic"]
            except KeyError:
                print(f"    {corpus}: unexpected output: {truncate(single_result)}")


def simple_query_summary(corpora, version):
    batch_size = 100
    all_results = {"hits": 0, "corpus_hits": {}, "kwic": [], "corpora_processed": 0}
    for i in range(len(corpora) // batch_size + 1):
        batch_start = i * batch_size
        batch_stop = (i + 1) * batch_size
        batch = corpora[batch_start:batch_stop]
        starttime = time.time()
        done = False
        try:
            result = make_simple_query(batch, version)
        except urllib.error.HTTPError:
            print(
                f"    some corpora failed with an HTTPError in batch {batch_start + 1} - {batch_start + len(batch)}, retrying each one..."
            )
            iterate_batch(batch, all_results, version)
            done = True

        if not done and "ERROR" in result:
            print(
                f"    some corpora returned an ERROR in batch {batch_start + 1} - {batch_start + len(batch)}: {result['ERROR']}, locating failed corpora..."
            )
            iterate_batch(batch, all_results, version)
            done = True

        print(
            f"    queried corpora {batch_start + 1} - {batch_start + len(batch)} in {time_format(time.time()-starttime)}"
        )
        if not done:
            all_results["corpora_processed"] += len(batch)
            all_results["hits"] += int(result["hits"])
            all_results["corpus_hits"].update(result["corpus_hits"])
            all_results["kwic"] += result["kwic"]
    return {
        "hits": all_results["hits"],
        "corpus_hits": all_results["corpus_hits"],
        "kwic_summary": kwic_summary(all_results["kwic"]),
    }


def get_summary(version):
    starttime = time.time()
    result = corpora_from_info(get_info(version))
    print(
        f"  got info with {len(result['corpora'])} total corpora, of which {len(result['protected_corpora'])} protected and {len(result['public_corpora'])} public, in {time_format(time.time()-starttime)}"
    )
    starttime = time.time()
    result["simple_query_summary"] = simple_query_summary(
        result["public_corpora"], version
    )
    print(
        f"  queried all {len(result['public_corpora'])} corpora in {time_format(time.time()-starttime)} with {len(result['simple_query_summary']['corpus_hits'])} corpora working correctly"
    )
    return result


def scan_korp(source):
    if source == "old_korp":
        return get_summary(version=1)
    elif source == "new_korp":
        return get_summary(version=2)
    else:
        return json.load(open(source))


def report_differences(first, second, args):
    if args.logfile:
        log_fobj = open(args.logfile, "w")
    else:
        log_fobj = open("/dev/null", "w")

    cmp1 = len(first["corpora"])
    cmp2 = len(second["corpora"])
    failed_ncorp = cmp1 != cmp2
    report(
        f"Got {cmp1} corpora in {args.first}, {cmp2} corpora in {args.second}",
        log_fobj,
        failed_ncorp,
    )

    first_corpora_s = set(first["corpora"])
    second_corpora_s = set(second["corpora"])
    failed = first_corpora_s != second_corpora_s
    if not failed_ncorp and not failed:
        report(f"Corpora names match", failed)
    else:
        cmp1 = first_corpora_s.difference(second_corpora_s)
        cmp2 = second_corpora_s.difference(first_corpora_s)
        report(
            f"Corpora sets differ: {cmp1} missing from {args.second}, {cmp2} missing from {args.first}",
            log_fobj,
            failed,
        )

    cmp1 = len(first["public_corpora"])
    cmp2 = len(second["public_corpora"])
    failed = cmp1 != cmp2
    report(
        f"Got {cmp1} public corpora in {args.first}, {cmp2} public corpora in {args.second}",
        log_fobj,
        failed,
    )

    cmp1 = len(first["protected_corpora"])
    cmp2 = len(second["protected_corpora"])
    failed = cmp1 != cmp2
    report(
        f"Got {cmp1} protected corpora in {args.first}, {cmp2} protected corpora in {args.second}",
        log_fobj,
        failed,
    )

    cmp1 = first["simple_query_summary"]["hits"]
    cmp2 = second["simple_query_summary"]["hits"]
    failed = cmp1 != cmp2
    report(
        f"Got {cmp1} query hits in {args.first}, {cmp2} query hits in {args.second}",
        log_fobj,
        failed,
    )

    first_corpus_hits_s = set(first["simple_query_summary"]["corpus_hits"].keys())
    second_corpus_hits_s = set(second["simple_query_summary"]["corpus_hits"].keys())
    for corpus in first_corpus_hits_s.intersection(second_corpus_hits_s):
        cmp1 = int(first["simple_query_summary"]["corpus_hits"][corpus])
        cmp2 = int(second["simple_query_summary"]["corpus_hits"][corpus])
        failed = cmp1 != cmp2
        report(
            f"In {corpus}, got {cmp1} query hits in {args.first}, {cmp2} query hits in {args.second}",
            log_fobj,
            failed,
        )

    # cmp1 = first["simple_query_summary"]["kwic_summary"]["charsum"]
    # cmp2 = second["simple_query_summary"]["kwic_summary"]["charsum"]
    # failed = cmp1 != cmp2
    # report(
    #     f"Got {cmp1} chars in hits in {args.first}, {cmp2} in {args.second}", log_fobj, failed
    # )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--first",
        default="old_korp",
        help="old_korp (default), new_korp or filename with json dump",
    )
    argparser.add_argument(
        "--second",
        default="new_korp",
        help="old_korp, new_korp (default), filename with json dump or none",
    )
    argparser.add_argument(
        "--outfile-first", help="Filename in which to write dump from --first"
    )
    argparser.add_argument(
        "--outfile-second", help="Filename in which to write dump from --first"
    )
    argparser.add_argument(
        "--logfile", help="Filename in which to write log from comparison"
    )
    args = argparser.parse_args()

    print()
    starttime = time.time()
    print(f"Getting summary from {args.first}... ")
    first_results = scan_korp(args.first)
    print(f"Completed in {time_format(time.time()-starttime)}")

    if args.outfile_first != None:
        with open(args.outfile_first, "w") as outfile_obj:
            json.dump(first_results, outfile_obj)

    print()

    if args.second == "none":
        exit()

    starttime = time.time()
    print(f"Getting summary from {args.second}... ")
    second_results = scan_korp(args.second)
    print(f"Completed in {time_format(time.time()-starttime)}")
    print()

    if args.outfile_second != None:
        with open(args.outfile_second, "w") as outfile_obj:
            json.dump(second_results, outfile_obj)

    report_differences(first_results, second_results, args)
