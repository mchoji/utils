#!/usr/bin/env python3
# MIT License
# 
# Copyright (c) 2021 M. Choji
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Fetch data from Internet and generate wordlists for subdomains or URIs
"""

import argparse
import logging
import tldextract
from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
        description="Fetch data from Internet and generate subdomain or URI wordlists")
parser.add_argument(
        "type",
        help="Type of wordlist to generate",
        choices=["sub", "uri"],
        )
parser.add_argument(
        "-s",
        "--silent",
        help="Ommit logging messages",
        action="store_true",
        )
parser.add_argument(
        "-c",
        "--count",
        help="Show output with count for each entry",
        action="store_true",
        )
parser.add_argument(
        "--days",
        help="Fetch data from these days (only valid for 'sub')",
        metavar="YYYY-MM-DD",
        nargs="+",
        )

args = parser.parse_args()


def get_umbrella_data(days: list = None):
    if days is None:
        logging.info("Downloading most recent umbrella data")
        resp = urlopen("https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip")
        zipfile = ZipFile(BytesIO(resp.read()))
        lines = zipfile.open(zipfile.namelist()[0]).readlines()
    else:
        lines = []
        for day in days:
            logging.info("Downloading umbrella data from %s", day)
            resp = urlopen(f"https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m-{day}.csv.zip")
            zipfile = ZipFile(BytesIO(resp.read()))
            lines.extend(zipfile.open(zipfile.namelist()[0]).readlines())

    return list(map(lambda x: x.decode('UTF-8').strip().split(',')[1], lines))



def gen_sub_list(hosts: list):
    subs_list = list(map(lambda x: tldextract.extract(x).subdomain, hosts))
    for sub in subs_list:
        if '.' in sub:
            subs_list.extend(sub.split('.'))
    return Counter(subs_list).most_common()


result = None
if args.type == "sub":
    result = gen_sub_list(get_umbrella_data(args.days))

if result is None:
    logging.error("An unexpected error has occurred")
    exit(1)
for res in result:
    if args.count:
        print(f"{res[1]} {res[0]}")
    else:
        print(res[0])
